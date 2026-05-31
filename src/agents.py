import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
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


def answer(question: str, pandas_agent, rag_chain) -> dict:
    route = route_question(question)
    print(f"[Router → {route}]")

    if route == "structured":
        result = pandas_agent.invoke(question)
        return {
            "answer": result["output"],
            "route": "structured",
            "sources": ["superstore_clean.csv"],
        }
    else:
        result = rag_chain.invoke(question)
        sources = list({d.metadata.get("doc_name", "unknown")
                        for d in result["source_documents"]})
        return {
            "answer": result["result"],
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

    print("\nInsightForge CLI ready. Type 'quit' to exit.\n")
    while True:
        question = input("Question: ").strip()
        if question.lower() == "quit":
            break
        result = answer(question, pandas_agent, rag_chain)
        print(f"\nAnswer: {result['answer']}")
        print(f"Route:   {result['route']}")
        print(f"Sources: {', '.join(result['sources'])}\n")


if __name__ == "__main__":
    run_unified_cli()
