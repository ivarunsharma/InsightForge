import os
from langchain_community.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

SUPPORTED_EXTENSIONS = {".txt", ".docx", ".pdf"}


def load_all_documents(data_dir=DATA_DIR):
    documents = []

    for filename in sorted(os.listdir(data_dir)):
        filepath = os.path.join(data_dir, filename)

        if not os.path.isfile(filepath):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            continue

        if ext == ".txt":
            loader = TextLoader(filepath, encoding="utf-8")
        elif ext == ".docx":
            loader = Docx2txtLoader(filepath)
        elif ext == ".pdf":
            loader = PyPDFLoader(filepath)

        try:
            docs = loader.load()
            for doc in docs:
                doc.metadata["file_type"] = ext.lstrip(".")
                doc.metadata["doc_name"] = filename
            documents.extend(docs)
            print(f"  Loaded: {filename} ({len(docs)} page(s))")
        except Exception as e:
            print(f"  Warning: could not load {filename} — {e}")

    print(f"\nTotal documents loaded: {len(documents)}")
    return documents


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(documents)
    print(f"Total chunks: {len(chunks)}")
    return chunks
