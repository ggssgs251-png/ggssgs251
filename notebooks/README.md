# 📓 Jupyter Notebooks

This directory contains Jupyter notebooks for exploring and testing the
ggssgs251 multi-agent system.

## Notebooks

| Notebook | Purpose |
|----------|---------|
| `01_index_documents.ipynb` | Upload and index documents into the RAG knowledge base |
| `02_query_knowledge_base.ipynb` | Query the knowledge base and test RAG responses |
| `03_test_guardrails.ipynb` | Test the Guardrail Agent against various inputs |

## Prerequisites

- Backend server running: `uvicorn backend.app:app --reload --port 8000`
- Ollama running with `nomic-embed-text` model
- A registered user account

## How to Run

```bash
# Install Jupyter (if you don't have it)
pip install jupyter

# Launch Jupyter
jupyter notebook

# Or use VS Code
code notebooks/
```
