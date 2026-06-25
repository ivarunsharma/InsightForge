import pandas as pd
from collections import defaultdict
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.rag_pipeline import get_llm, load_vectorstore, build_rag_chain

ROUTER_SYSTEM = """You are a router for a business intelligence assistant.
Classify the user's question into exactly one of two categories:

structured — questions answerable from tabular sales data (CSV):
  numbers, aggregations, totals, averages, comparisons, trends, ranks,
  revenue, profit, discount, sales, customers, regions, categories, sub-categories

document — questions answerable from written documents:
  board meeting notes, annual reports, customer feedback, supplier contracts,
  memos, strategies, what someone said or discussed, qualitative findings

Reply with exactly one word: structured  or  document"""


def build_pandas_agent(llm, csv_path="data/superstore_clean.csv"):
    df = pd.read_csv(csv_path)
    return create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        allow_dangerous_code=True,
        agent_type="openai-tools",
    )


def _format_sources(context_docs) -> list[str]:
    pages_by_doc = defaultdict(set)
    for doc in context_docs:
        name = doc.metadata.get("doc_name", "unknown")
        page = doc.metadata.get("page")
        if page is not None:
            pages_by_doc[name].add(page + 1)  # PyPDFLoader is 0-indexed
        else:
            pages_by_doc.setdefault(name, set())
    sources = []
    for name, pages in pages_by_doc.items():
        if pages:
            sources.append(f"{name} (p. {', '.join(str(p) for p in sorted(pages))})")
        else:
            sources.append(name)
    return sources


_COMPLEX_WORDS = {"compare", "all", "across", "summarize", "list", "every",
                  "each", "between", "vs", "versus", "difference", "similarities"}


def _dynamic_k(question: str) -> int:
    words = question.lower().split()
    if len(words) > 20 or _COMPLEX_WORDS & set(words):
        return 8
    if len(words) >= 10:
        return 5
    return 3


def classify_intent(question: str, llm) -> str:
    response = llm.invoke([
        SystemMessage(content=ROUTER_SYSTEM),
        HumanMessage(content=question),
    ])
    label = response.content.strip().lower()
    return "structured" if "structured" in label else "document"


def answer(question: str, pandas_agent, vectorstore, llm, chat_history: list = None) -> dict:
    if chat_history is None:
        chat_history = []

    route = classify_intent(question, llm)
    k = _dynamic_k(question)
    print(f"[Router → {route}] [k={k}]")

    if route == "structured":
        if chat_history:
            history_lines = []
            for msg in chat_history[-6:]:
                role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
                history_lines.append(f"{role}: {msg.content}")
            augmented_question = (
                f"Previous conversation:\n{chr(10).join(history_lines)}\n\n"
                f"Current question: {question}"
            )
        else:
            augmented_question = question
        result = pandas_agent.invoke(augmented_question)
        return {
            "answer": result["output"],
            "route": "structured",
            "sources": ["superstore_clean.csv"],
        }
    else:
        rag_chain = build_rag_chain(vectorstore, k=k)
        result = rag_chain.invoke({"input": question, "chat_history": chat_history})
        sources = _format_sources(result["context"])
        return {
            "answer": result["answer"],
            "route": "document",
            "sources": sources,
        }


def run_csv_cli():
    llm = get_llm()
    agent = build_pandas_agent(llm)
    print("CSV Q&A ready. Type 'quit' to exit.\n")
    while True:
        question = input("Question: ").strip()
        if question.lower() == "quit":
            break
        result = agent.invoke(question)
        print(f"\nAnswer: {result['output']}\n")


def run_unified_cli():
    llm = get_llm()
    pandas_agent = build_pandas_agent(llm)
    vectorstore = load_vectorstore()
    chat_history = []

    print("\nInsightForge CLI ready. Type 'quit' to exit.\n")
    while True:
        question = input("Question: ").strip()
        if question.lower() == "quit":
            break
        result = answer(question, pandas_agent, vectorstore, llm, chat_history)
        print(f"\nAnswer: {result['answer']}")
        print(f"Route:   {result['route']}")
        print(f"Sources: {', '.join(result['sources'])}\n")
        chat_history.append(HumanMessage(content=question))
        chat_history.append(AIMessage(content=result["answer"]))
        chat_history = chat_history[-10:]


if __name__ == "__main__":
    run_unified_cli()
