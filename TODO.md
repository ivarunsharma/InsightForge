# InsightForge — Improvements

## Quick Wins (< 1 hr total)
- [x] Add `.dockerignore` (already present)
- [x] Error handling in Streamlit chat — show user-friendly message on LLM/agent failure (30 min)
- [x] Page numbers in RAG source citations (15 min)
- [x] Fix date parsing `UserWarning` in `data_cleaner.py` — specify explicit format strings

## Medium (1–3 hrs each)
- [x] Unify `.env` location for Docker (docker-compose.yml already uses `../.env`)
- [x] Skip cleaning if clean CSV is already current (hash check)
- [x] LLM-based intent classifier to replace keyword router
- [x] Dynamic `k` retrieval based on query complexity
- [x] Startup progress bar for first-run index build
- [x] Add tests for `src/rag_pipeline.py` and `src/agents.py`
- [x] Pin all dependency versions in `requirements.txt`
- [x] Add `healthcheck` to `docker-compose.yml`

## Larger (3+ hrs each)
- [ ] Hash-based incremental re-indexing (only re-embed changed/new docs)
- [ ] Persistent chat history (SQLite)
- [ ] Reorganise `data/` into `structured/` + `documents/` subdirs (needs path updates)
- [ ] GitHub Actions CI pipeline (pytest on every push)
