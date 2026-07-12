# 🤖 ggssgs251 — Multi-Agent AI System with RAG

An intelligent multi-agent AI system with **RAG-powered knowledge base**, **user authentication**, and a **modern web UI**. Chat with a team of AI specialists — Data Tutor and Code Advisor — augmented by your proprietary documents.

```
Frontend (React + shadcn/ui)  →  Backend (FastAPI)  →  Strands Agents (Python)
                                       │
                            ┌──────────┼──────────┐
                            │          │          │
                         SQLite    ChromaDB     Ollama
                        (users)   (vectors)   (LLM + embed)
```

## ✨ Features

- **🧠 Three AI Agents** — Orchestrator routes to Data Tutor or Code Advisor
- **📚 RAG Knowledge Base** — Upload PDF, DOCX, TXT, Markdown — agents answer from your data
- **🔐 User Auth** — Register/login with JWT tokens
- **🖥️ Modern Web UI** — React + shadcn/ui + Framer Motion
- **🛡️ 100% Local** — No cloud costs, no data leaves your machine
- **🔄 Dynamic Routing** — Swarm pattern agents hand off tasks to each other

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 20+** and **Bun** (or npm)
- **Ollama** with a pulled model

### 1. Install Ollama & Pull Models

```bash
# Install Ollama: https://ollama.ai
ollama pull llama3.1        # Primary LLM
ollama pull nomic-embed-text  # Embedding model for RAG
ollama serve                # Start the server
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install Python deps
pip install 'strands-agents[ollama]>=0.1.0' \
            'strands-agents-tools>=0.1.0' \
            'fastapi>=0.110.0' \
            'uvicorn[standard]>=0.27.0' \
            'python-multipart>=0.0.9' \
            'chromadb>=0.5.0' \
            'sqlalchemy>=2.0.0' \
            'pyjwt>=2.8.0' \
            'bcrypt>=4.1.0' \
            'pypdf2>=3.0.0' \
            'python-docx>=1.1.0' \
            'httpx>=0.27.0'

# Start the API server
uvicorn backend.app:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
bun install     # or: npm install
bun run dev     # or: npm run dev
```

### 4. Open the App

Navigate to **http://localhost:5173** in your browser.

## 🖥️ Architecture

```
┌──────────────────────────────────────────────────┐
│                    Frontend                       │
│         React + Vite + shadcn/ui                 │
│                                                   │
│  Landing │ Login │ Register │ Dashboard │ Chat   │
└──────────────────────┬───────────────────────────┘
                       │ HTTP (REST API)
                       ▼
┌──────────────────────────────────────────────────┐
│                   Backend (FastAPI)               │
│                                                   │
│  ┌─────┐  ┌──────┐  ┌───────┐  ┌───────────┐   │
│  │Auth │  │ Chat │  │  RAG  │  │ Knowledge  │   │
│  │Routes│  │Routes│  │Routes │  │  Mgmt     │   │
│  └──┬──┘  └──┬───┘  └──┬────┘  └─────┬─────┘   │
│     │        │         │             │          │
│  ┌──▼────────▼─────────▼─────────────▼──────┐   │
│  │           Strands Swarm                   │   │
│  │  ┌──────────┐  ┌────────┐  ┌──────────┐  │   │
│  │  │Orchestr. │  │  Data  │  │   Code   │  │   │
│  │  │          │  │  Tutor │  │  Advisor │  │   │
│  │  └──────────┘  └────────┘  └──────────┘  │   │
│  └───────────────────┬───────────────────────┘   │
│                      │                           │
│  ┌───────────────────┼───────────────────────┐   │
│  │        SQLite     │     ChromaDB          │   │
│  │     (users.db)    │  (vector store)       │   │
│  └───────────────────┴───────────────────────┘   │
└──────────────────────────────────────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │    Ollama     │
              │  llama3.1 +   │
              │ nomic-embed   │
              └───────────────┘
```

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login, returns JWT |
| `GET` | `/auth/me` | Get current user |
| `POST` | `/chat/message` | Send message to agents |
| `POST` | `/chat/reset` | Reset conversation |
| `POST` | `/rag/upload` | Upload a document for indexing |
| `POST` | `/rag/query` | Search the knowledge base |
| `GET` | `/rag/documents` | List indexed documents |
| `DELETE` | `/rag/documents/{name}` | Delete a document from index |

## 🗂️ Project Structure

```
ggssgs251/
├── pyproject.toml          # Python dependencies
├── src/                    # Agent code (Strands SDK)
│   ├── main.py             # CLI entry point (optional)
│   ├── orchestrator.py     # Swarm orchestration
│   ├── agents/
│   │   ├── data_tutor.py   # Data Tutor agent
│   │   └── code_advisor.py # Code Advisor agent
│   └── tools/
│       └── custom_tools.py # Agent tools
├── backend/                # FastAPI backend
│   ├── app.py              # FastAPI app entry
│   ├── config.py           # Settings
│   ├── database.py         # SQLAlchemy setup
│   ├── models.py           # User model
│   ├── schemas.py          # Pydantic schemas
│   ├── auth.py             # JWT auth
│   ├── rag_engine.py       # RAG pipeline
│   ├── routes_chat.py      # Chat API
│   └── routes_rag.py       # RAG API
├── frontend/               # React + Vite
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── src/
│       ├── App.tsx
│       ├── pages/          # Landing, Login, Register, Dashboard, Chat
│       └── lib/            # API client, auth context, utils
├── data/                   # Auto-created: DB, uploads, chroma_db
└── README.md
```

## 🛠️ Customizing Agents

Edit agent system prompts in `src/agents/data_tutor.py` or `src/agents/code_advisor.py`.

Add new tools in `src/tools/custom_tools.py` using the `@tool` decorator:

```python
from strands import tool

@tool
def custom_tool(param: str) -> str:
    """Description for the LLM."""
    return f"Result: {param}"
```

## 📄 License

MIT
