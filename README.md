# InsightForge — AI Business Intelligence Assistant

An AI-powered BI assistant for TechRetail Corporation. Ask any question in plain English — InsightForge routes it to the right engine, computes or retrieves the answer, and returns a response with sources cited.

---

## What It Does

- **Structured questions** ("What is total profit by region?") → Pandas DataFrame Agent runs real Python code on 7,010 rows of cleaned sales data
- **Document questions** ("What did the board discuss about Q4?") → RAG chain searches 407 indexed chunks from 14 business documents (TXT, DOCX, PDF)
- **Conversational follow-ups** work naturally — ask "What about the East?" after a prior question and the system understands the context
- An **LLM-based intent classifier** automatically decides which engine to use — no manual selection required
- **Dynamic retrieval** adjusts how many document chunks are fetched based on query complexity
- **Page-level source citations** show exactly which document and page number each answer came from
- A **Streamlit UI** with live charts, sidebar metrics, chat interface, and a first-run progress bar
- **Graceful error handling** in chat — user-friendly messages with collapsible error details

---

## Project Structure

```
InsightForge/
├── app.py                    ← Streamlit web app
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example              ← copy to .env and fill in your Azure keys
├── src/
│   ├── data_cleaner.py       ← cleans superstore_messy.csv → superstore_clean.csv (hash-skips if unchanged)
│   ├── document_loader.py    ← loads TXT/DOCX/PDF, chunks into 800-char pieces
│   ├── rag_pipeline.py       ← Chroma vector store + LCEL RAG chain
│   ├── agents.py             ← Pandas agent + LLM intent classifier + dynamic k + conversation memory
│   └── visualizations.py    ← 5 chart functions + auto-insights
├── data/                     ← raw + clean CSV, TXT, DOCX, PDF documents
└── chroma_db/                ← Chroma vector store (built on first run, gitignored)
```

---

## Setup

### 1. Clone and activate virtual environment

```bash
git clone <repo-url>
cd InsightForge
python -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure `.env`

Copy `.env.example` to `.env` (one level above `InsightForge/`, same level as `venv/`):

```bash
cp .env.example ../.env
```

Fill in your Azure OpenAI credentials:

```
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your_gpt_deployment_name
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-01
```

---

## Running the App

### Option A — Streamlit (development)

```bash
source ../venv/bin/activate
streamlit run app.py
```

Opens at `http://localhost:8501`. On first run, a step-by-step progress bar tracks index building (~1–3 min). Subsequent runs load from disk instantly.

### Option B — Docker

```bash
docker compose up --build
```

Opens at `http://localhost:8501`. The `chroma_db/` and `data/` directories are volume-mounted so the pre-built index is reused inside the container. A Docker healthcheck monitors app readiness at `/_stcore/health`.

### Option C — CLI only (no UI)

```bash
# Unified CLI (routes automatically)
source ../venv/bin/activate
python -m src.agents

# RAG documents only
python -m src.rag_pipeline
```

---

## Sample Questions

| Question | Route | Source |
|---|---|---|
| What is total revenue by region? | Pandas Agent | superstore_clean.csv |
| Which sub-category has the worst profit margin? | Pandas Agent | superstore_clean.csv |
| Compare Technology vs Furniture sales | Pandas Agent | superstore_clean.csv |
| What did the board discuss about Q4 performance? | RAG | board_presentation_notes_Dec2017.pdf |
| What are the main customer complaints about shipping? | RAG | customer_feedback_notes.txt |
| Are there any supplier compliance issues? | RAG | supplier_contracts_summary.docx |

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Azure OpenAI GPT-4 |
| Embeddings | Azure OpenAI Ada-002 (1536-dim) |
| Vector store | Chroma (persisted to `chroma_db/`) |
| Structured agent | LangChain Pandas DataFrame Agent |
| Document loader | LangChain TextLoader / Docx2txtLoader / PyPDFLoader |
| Web UI | Streamlit |
| Data processing | Pandas |
| Containerization | Docker + Docker Compose |

---

## Environment Notes

- `.env` must live one level **above** `InsightForge/` (same level as `venv/`). All modules use `load_dotenv(find_dotenv())` to locate it.
- `chroma_db/` is gitignored — build it locally once with `python -m src.rag_pipeline`, then volume-mount into Docker.
- Python 3.11+ required.
