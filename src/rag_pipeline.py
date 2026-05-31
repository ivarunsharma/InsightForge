import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv(find_dotenv(), override=True)

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

SYSTEM_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a business intelligence assistant for TechRetail Corporation.
Answer the question using ONLY the information in the context below.
If the answer is not in the context, say "I don't have enough information in my documents to answer that."
Always mention which document your answer comes from.

Context:
{context}

Question: {question}

Answer:""",
)


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


def build_vectorstore(chunks):
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
    )
    print(f"Vector store built: {vectorstore._collection.count()} chunks indexed")
    return vectorstore


def load_vectorstore():
    embeddings = get_embeddings()
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )
    print(f"Vector store loaded: {vectorstore._collection.count()} chunks")
    return vectorstore


def build_rag_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    return RetrievalQA.from_chain_type(
        llm=get_llm(),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": SYSTEM_PROMPT},
    )


def run_rag_cli():
    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        print("Building index for the first time...")
        from src.document_loader import load_all_documents, chunk_documents
        docs = load_all_documents()
        chunks = chunk_documents(docs)
        vs = build_vectorstore(chunks)
    else:
        vs = load_vectorstore()

    chain = build_rag_chain(vs)
    print("\nDocument Q&A ready. Type 'quit' to exit.\n")

    while True:
        question = input("Question: ").strip()
        if question.lower() == "quit":
            break
        result = chain.invoke(question)
        print(f"\nAnswer: {result['result']}")
        sources = list({d.metadata.get("doc_name", "unknown") for d in result["source_documents"]})
        print(f"Sources: {', '.join(sources)}\n")


if __name__ == "__main__":
    run_rag_cli()
