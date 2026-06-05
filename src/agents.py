import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_core.messages import HumanMessage, AIMessage
from src.rag_pipeline import get_llm, load_vectorstore, build_rag_chain

STRUCTURED_KEYWORDS = [
    "total", "sum", "average", "mean", "count", "how many", "number of",
    "highest", "lowest", "most", "least", "top", "bottom", "best", "worst",
    "revenue", "sales", "profit", "margin", "discount",
    "compare", "trend", "growth", "change", "percentage",
    "by region", "by category", "by segment", "per", "in 2017", "in 2016",
]

DOCUMENT_KEYWORDS = [
    "report", "said", "mentioned", "discussed", "board", "meeting",
    "contract", "supplier", "feedback", "memo", "presentation",
    "recommendation", "strategy", "what did", "according to",
]


def build_pandas_agent(llm, csv_path="data/superstore_clean.csv"):
    df = pd.read_csv(csv_path)
    return create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        allow_dangerous_code=True,
        agent_type="openai-tools",
    )


def route_question(question: str) -> str:
    q = question.lower()
    s_score = sum(1 for kw in STRUCTURED_KEYWORDS if kw in q)
    d_score = sum(1 for kw in DOCUMENT_KEYWORDS if kw in q)
    return "structured" if s_score > d_score else "document"


def answer(question: str, pandas_agent, rag_chain, chat_history: list = None) -> dict:
    if chat_history is None:
        chat_history = []

    route = route_question(question)
    print(f"[Router → {route}]")

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
        result = rag_chain.invoke({"input": question, "chat_history": chat_history})
        sources = list({d.metadata.get("doc_name", "unknown")
                        for d in result["context"]})
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
    rag_chain = build_rag_chain(vectorstore)
    chat_history = []

    print("\nInsightForge CLI ready. Type 'quit' to exit.\n")
    while True:
        question = input("Question: ").strip()
        if question.lower() == "quit":
            break
        result = answer(question, pandas_agent, rag_chain, chat_history)
        print(f"\nAnswer: {result['answer']}")
        print(f"Route:   {result['route']}")
        print(f"Sources: {', '.join(result['sources'])}\n")
        chat_history.append(HumanMessage(content=question))
        chat_history.append(AIMessage(content=result["answer"]))
        chat_history = chat_history[-10:]


if __name__ == "__main__":
    run_unified_cli()
