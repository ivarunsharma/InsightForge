import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from src.rag_pipeline import get_llm


def build_pandas_agent(llm, csv_path="data/superstore_clean.csv"):
    df = pd.read_csv(csv_path)
    return create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        allow_dangerous_code=True,
        agent_type="openai-tools",
    )


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


if __name__ == "__main__":
    run_csv_cli()
