# InsightForge — AI Business Intelligence Assistant

> **What it covers:** LangChain, RAG, and Azure OpenAI basics.

---

## What Is This Project?

Imagine you're a business analyst at **TechRetail Corporation**. Your boss drops a folder on your desk with:

- A messy spreadsheet of 10,000 sales transactions
- PDFs of annual reports and board meeting notes
- Word documents with supplier contracts and meeting minutes
- Text files with quarterly sales reports
- JPEG charts from previous presentations

Your boss says: **"I need answers. Which region is most profitable? What's hurting our margins? What do our customers say about shipping?"**

Normally you'd spend days manually reading all those files. **InsightForge automates that.** You type a question in plain English, and the system:

1. Reads and cleans all the messy data automatically
2. Searches the right documents for relevant information
3. Asks an AI (GPT via Azure) to synthesize an answer
4. Shows you charts and a clean dashboard

---

## The Big Picture — How It All Connects

```
Your Data Files (CSV, PDF, DOCX, TXT, JPG)
        |
        v
[Phase 1] Data Cleaning (Pandas)
        |
        v
[Phase 2] Document Loading & Chunking (LangChain)
        |
        v
[Phase 3] Embeddings → FAISS Vector Store (RAG)
        |
        v
[Phase 4] LangChain Agents (Pandas Agent + RAG Chain)
        |
        v
[Phase 5] Azure OpenAI GPT answers your questions
        |
        v
[Phase 6] Streamlit Web UI + Charts
        |
        v
[Phase 7] Put it all together → Final Working System
```