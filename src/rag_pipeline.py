import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

load_dotenv(find_dotenv(), override=True)


def get_llm():
    return AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0,
    )


def get_embeddings():
    return AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )


def test_connection():
    print("Testing Azure LLM...")
    llm = get_llm()
    response = llm.invoke("Say 'Azure connected successfully'")
    print(response.content)

    print("\nTesting embeddings...")
    emb = get_embeddings()
    vector = emb.embed_query("test")
    print(f"Embedding dimension: {len(vector)}")


if __name__ == "__main__":
    test_connection()
