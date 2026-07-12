# 🤖 ggssgs251 — Multi-Agent AI System with RAG

An intelligent multi-agent AI system powered by the **Strands Agents SDK**, augmented with **RAG (Retrieval-Augmented Generation)** over your proprietary documents, complete with **user authentication** and a **Python web UI**.

Chat with a team of AI specialists — a **Data Tutor** and **Code Advisor** — that can answer questions from your own data.

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start: Docker (Recommended)](#-quick-start-docker-recommended)
- [🛠️ Local Development Setup](#️-local-development-setup)
- [📡 API Endpoints](#-api-endpoints)
- [🗂️ Project Structure](#️-project-structure)
- [🐳 Docker Reference](#-docker-reference)
- [🔧 Configuration](#-configuration)
- [👤 Adding Custom Agents](#-adding-custom-agents)
- [📄 License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Three AI Agents** | Orchestrator routes requests to Data Tutor or Code Advisor |
| 📚 **RAG Knowledge Base** | Upload PDF, DOCX, TXT, Markdown — agents answer from your data |
| 🔐 **User Authentication** | Register/login with JWT tokens, bcrypt password hashing |
| 🖥️ **Python Web UI** | FastAPI Jinja2 templates + Tailwind CSS — **no Node.js required** |
| 🛡️ **100% Local & Private** | No cloud costs, no data leaves your machine |
| 🔄 **Dynamic Agent Routing** | Swarm pattern — agents dynamically hand off tasks |
| 📄 **Multi-format Upload** | PDF, Word (.docx), Plain Text (.txt), Markdown (.md) |
| 🔎 **Semantic Search** | ChromaDB vector search over your indexed documents |
| 🐳 **Dockerized** | One-command setup with Docker Compose |
| 🔒 **Guardrail Agent** | Blocks PII, profanity, hate speech before reaching the LLM |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Server (Port 8000)                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Frontend (Jinja2 Templates + Tailwind CSS)                 ││
│  │  Landing → Login/Register → Dashboard → Chat                ││
│  └──────────────────────────┬──────────────────────────────────┘│
│                             │ (same origin — no CORS needed)     │
│  ┌──────────────────────────▼──────────────────────────────────┐│
│  │                    API Routes                                ││
│  │                                                              ││
│  │  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ ││
│  │  │  Auth   │  │  Chat    │  │   RAG    │  │  Guardrail    │ ││
│  │  │ Routes  │  │ Routes   │  │  Routes  │  │  Checker      │ ││
│  │  └────┬────┘  └────┬─────┘  └────┬─────┘  └───────┬──────┘ ││
│  │       │            │             │                  │        ││
│  │  ┌────▼────────────▼─────────────▼──────────────────▼─────┐ ││
│  │  │                    Strands Swarm                       │ ││
│  │  │  ┌────────────────┐  ┌────────────┐  ┌──────────────┐ │ ││
│  │  │  │  Orchestrator  │  │ Data Tutor │  │ Code Advisor │ │ ││
│  │  │  │  (Entry point) │  │  (Stats)   │  │ (Coding)     │ │ ││
│  │  │  └────────────────┘  └────────────┘  └──────────────┘ │ ││
│  │  └──────────────────────────┬────────────────────────────┘ ││
│  │                             │                               ││
│  │  ┌──────────────────────────┼───────────────────────────┐  ││
│  │  │      SQLite (users.db)   │     ChromaDB (vectors)    │  ││
│  │  │      User accounts       │     Document embeddings   │  ││
│  │  └──────────────────────────┴───────────────────────────┘  ││
│  └────────────────────────────────────────────────────────────┘│
└──────────────────────────┬─────────────────────────────────────┘
                           │
              ┌────────────▼──────────────────────────────┐
              │     Ollama (Port 11434)                    │
              │  ┌──────────┐  ┌───────────────────────┐  │
              │  │ tinyllama │  │ nomic-embed-text      │  │
              │  │  (LLM)   │  │  (embeddings)         │  │
              │  └──────────┘  └───────────────────────┘  │
              └───────────────────────────────────────────┘
```

### Data Flow

```
User Uploads Document
  → File saved to /app/data/uploads/
  → Text extracted (PDF/DOCX/TXT/MD parser)
  → Text chunked into 500-char segments
  → Chunks embedded via Ollama (nomic-embed-text)
  → Vectors stored in ChromaDB

User Asks Question
  → Guardrail checks for PII/profanity/hate speech
  → Question embedded via Ollama
  → ChromaDB semantic search (top-k results)
  → Relevant chunks formatted as context
  → Context + question sent to Strands Swarm
  → Orchestrator routes to Data Tutor or Code Advisor
  → Agent generates answer with RAG context
  → Response returned to UI
```

---

## 🚀 Quick Start: Docker (Recommended)

The fastest way to get everything running is with Docker Compose. This starts two services:

1. **Ollama** — LLM server (automatically pulls `tinyllama` and `nomic-embed-text`)
2. **Backend** — FastAPI + Agent Swarm + ChromaDB + Jinja2 web UI (all in one container)

### Prerequisites

- **Docker** (version 24+) and **Docker Compose** (version 2.20+)
  - [Install Docker Desktop](https://docs.docker.com/get-docker/) (includes Compose)
- **~8 GB free RAM** (for running local LLM in Docker)
- **~5 GB free disk space** (for Docker images and LLM models)

### Step 1: Clone & Configure

```bash
git clone https://github.com/ggssgs251-png/ggssgs251.git
cd ggssgs251

# (Optional) Set a secure secret key
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env
```

### Step 2: Build & Start

```bash
# Build and start all services
docker compose up --build

# Or run in background
docker compose up --build -d
```

### Step 3: Wait for Startup

First startup takes **2-5 minutes** (Docker build + Ollama model downloads).

Watch the logs:
```bash
docker compose logs -f
```

### Step 4: Open the App

```
http://localhost:8000
```

### Step 5: Create an Account

1. Click **"Get Started"** or navigate to `/register`
2. Enter your email, username, and password
3. You'll be auto-logged in and redirected to the Dashboard

### Docker Quick Commands

```bash
docker compose up -d          # Start all services
docker compose logs -f        # View logs
docker compose down           # Stop services
docker compose down -v        # Stop + delete data (wipes everything!)
docker compose build backend  # Rebuild backend
docker compose ps             # Check service health
```

---

## 🛠️ Local Development Setup

If you prefer to run without Docker.

### Prerequisites

- **Python 3.10+**
- **Ollama** — [install from ollama.ai](https://ollama.ai)

### Step 1: Install Ollama & Pull Models

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the LLM and embedding models
ollama pull tinyllama
ollama pull nomic-embed-text

# Start the Ollama server
ollama serve
```

Verify Ollama:
```bash
curl http://localhost:11434/api/tags
# Should return a JSON list of models
```

### Step 2: Set Up Python

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install all Python dependencies
pip install -e .
# OR install from pyproject.toml:
pip install strands-agents>=0.1.0 \
            ollama>=0.6.0 \
            fastapi>=0.110.0 \
            uvicorn[standard]>=0.27.0 \
            chromadb>=0.5.0 \
            sqlalchemy>=2.0.0 \
            pyjwt>=2.8.0 \
            bcrypt>=4.1.0 \
            pypdf2>=3.0.0 \
            python-docx>=1.1.0 \
            httpx>=0.27.0 \
            jinja2>=3.1.0 \
            aiofiles>=24.1.0
```

### Step 3: Start the Server

```bash
# Start the API server (serves both the API and the web UI)
uvicorn backend.app:app --reload --port 8000
```

### Step 4: Open the App

```
http://localhost:8000
```

No frontend build step needed — the HTML templates are served directly by FastAPI.

### Running Tests

```bash
# Activate venv first
source .venv/bin/activate

# Run guardrail tests
python -m pytest backend/tests/test_guardrails.py -v

# Run linting
ruff check backend/ src/
```

### Using Jupyter Notebooks

```bash
# Start Jupyter for interactive RAG/guardrail testing
bash scripts/start_jupyter.sh
```

---

## 📡 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/` | No | Landing page |
| `GET` | `/login` | No | Login page |
| `GET` | `/register` | No | Registration page |
| `GET` | `/dashboard` | No | Dashboard page |
| `GET` | `/chat` | No | Chat page |
| `POST` | `/auth/register` | No | Register a new user |
| `POST` | `/auth/login` | No | Login, returns JWT token |
| `GET` | `/auth/me` | Yes | Get current user profile |
| `POST` | `/chat/message` | Yes | Send message to AI agents with RAG |
| `POST` | `/rag/upload` | Yes | Upload & index a document |
| `POST` | `/rag/query` | Yes | Search the knowledge base |
| `GET` | `/rag/documents` | Yes | List all indexed documents |
| `DELETE` | `/rag/documents/{filename}` | Yes | Delete a document from the index |
| `GET` | `/health` | No | Health check |
| `POST` | `/guardrail/check?text=...` | No | Test the guardrail |

### API Example: Register & Chat

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"testuser","password":"password123"}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# 3. Chat with agents (use the returned token)
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"message":"What is a p-value?"}'

# 4. Upload a document
curl -X POST http://localhost:8000/rag/upload \
  -H "Authorization: Bearer eyJ..." \
  -F "file=@report.pdf"

# 5. Query the knowledge base
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"query":"What does our report say about revenue?"}'
```

---

## 🐳 Docker Reference

### Services

| Service | Container Name | Image | Internal Port | External Port | Depends On |
|---------|---------------|-------|---------------|---------------|------------|
| **ollama** | `ggssgs251-ollama` | `ollama/ollama:latest` | 11434 | 11434 | — |
| **backend** | `ggssgs251-backend` | Custom (Python 3.11) | 8000 | 8000 | ollama (healthy) |

The backend serves both the REST API **and** the Jinja2 web UI on the same port.

### Volumes

| Volume | Mount Point | Purpose |
|--------|------------|---------|
| `ggssgs251_ollama_data` | `/root/.ollama` | Persists LLM models across restarts |
| `ggssgs251_backend_data` | `/app/data` | Persists SQLite DB, ChromaDB vectors, uploaded files |

### Network

All services on a shared bridge network `ggssgs251-net`, reachable by container name.

### Dockerfile

`backend/Dockerfile` — Multi-stage Python build:

| Stage | Base Image | Purpose |
|-------|-----------|---------|
| `builder` | `python:3.11-slim` | Installs all Python dependencies with build tools |
| `runtime` | `python:3.11-slim` | Copies installed packages + app code + prompts (~200 MB) |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-me-in-production...` | JWT signing secret (REQUIRED to change in production) |
| `OLLAMA_HOST` | `http://ollama:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `tinyllama` | LLM model for agent responses |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Model for generating document embeddings |
| `CORS_ORIGINS` | `http://localhost:8000` | Allowed CORS origins |

---

## 🔧 Configuration

### Changing the LLM Model

Edit `backend/config.py` or set the `OLLAMA_MODEL` env var:

```bash
OLLAMA_MODEL=mistral docker compose up -d
```

You'll also need to pull the model:
```bash
ollama pull mistral
```

### Adjusting RAG Parameters

Edit `backend/config.py`:

```python
CHUNK_SIZE = 500          # Characters per document chunk
CHUNK_OVERLAP = 50        # Overlap between consecutive chunks
DEFAULT_RAG_RESULTS = 5   # Number of chunks to retrieve per query
RAG_MIN_SCORE = 0.3       # Minimum similarity score (0-1)
```

### Adjusting Guardrail Sensitivity

Edit `backend/guardrails/rules.py`:

```python
BLOCK_THRESHOLD = 10      # Lower = stricter, Higher = more permissive
```

---

## 🗂️ Complete Project Structure

```
ggssgs251/
│
├── docker-compose.yml           # Docker Compose — 2 services
├── pyproject.toml               # Python package + dependencies
├── README.md                    # This file
├── LICENSE                      # MIT License
├── .gitignore
│
├── backend/
│   ├── Dockerfile               # Multi-stage Python build
│   ├── app.py                   # FastAPI entry point + Jinja2 routes
│   ├── config.py                # All configuration settings
│   ├── database.py              # SQLAlchemy + SQLite setup
│   ├── models.py                # User SQLAlchemy model
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── auth.py                  # JWT auth, bcrypt, /auth/* routes
│   ├── rag_engine.py            # ChromaDB RAG pipeline (index + search)
│   ├── logging_config.py        # Structured stage-level logging
│   ├── routes_chat.py           # /chat/* endpoints with agent integration
│   ├── routes_rag.py            # /rag/* endpoints for document management
│   │
│   ├── guardrails/
│   │   ├── __init__.py
│   │   ├── checker.py           # GuardrailChecker scoring engine
│   │   └── rules.py             # Regex patterns + blocklists
│   │
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html            # Base layout (Tailwind CSS)
│   │   ├── landing.html         # Landing page with hero + features
│   │   ├── login.html           # Login form
│   │   ├── register.html        # Registration form
│   │   ├── dashboard.html       # Document upload + management UI
│   │   └── chat.html            # Full chat UI with sidebar
│   │
│   ├── static/                  # Static assets (CSS, JS, images)
│   │   ├── css/
│   │   └── js/
│   │
│   └── tests/
│       ├── __init__.py
│       └── test_guardrails.py   # 11 pytest tests (no Ollama needed)
│
├── src/                          # Python agent code
│   ├── main.py                  # CLI entry point
│   ├── orchestrator.py          # Strands Swarm setup + orchestration
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── data_tutor.py        # Data Tutor agent prompt + tools
│   │   └── code_advisor.py      # Code Advisor agent prompt + tools
│   └── tools/
│       ├── __init__.py
│       └── custom_tools.py      # @tool-decorated functions
│
├── prompts/                      # Editablesystem prompts (.md)
│   ├── README.md
│   ├── orchestrator.md
│   ├── data_tutor.md
│   ├── code_advisor.md
│   └── guardrail_agent.md
│
├── notebooks/                    # Jupyter notebooks for RAG testing
│   ├── README.md
│   ├── 01_index_documents.ipynb
│   ├── 02_query_knowledge_base.ipynb
│   └── 03_test_guardrails.ipynb
│
├── scripts/
│   └── start_jupyter.sh         # Launch Jupyter with project kernel
│
├── data/                        # Auto-created at runtime (gitignored)
│   ├── uploads/                 # Uploaded documents
│   ├── chroma_db/               # ChromaDB persistent storage
│   ├── sample_docs/             # Sample documents for testing
│   ├── logs/                    # Stage-level log files
│   └── ggssgs251.db            # SQLite user database
│
└── .github/
    └── workflows/
        ├── ci.yml               # CI: ruff + pytest on every push
        └── docker.yml           # CD: build & push Docker image (ghcr.io)
```

---

## 👤 Adding Custom Agents

### 1. Create a New Agent

Create `src/agents/custom_agent.py`:

```python
"""Custom specialist agent."""

from strands import Agent
from strands.models.ollama import OllamaModel
from src.tools import some_tool

SYSTEM_PROMPT = """You are a specialist in [domain].
Help users with [specific tasks].
Hand off to other agents when appropriate."""

def create_custom_agent(model: OllamaModel) -> Agent:
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[some_tool],
    )
```

### 2. Add It to the Swarm

Edit `src/orchestrator.py`:

```python
from src.agents.custom_agent import create_custom_agent

def create_swarm(model: OllamaModel) -> Swarm:
    data_tutor = create_data_tutor(model)
    code_advisor = create_code_advisor(model)
    custom_agent = create_custom_agent(model)  # 👈 New agent

    orchestrator = Agent(
        model=model,
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
    )

    swarm = Swarm(
        nodes=[orchestrator, data_tutor, code_advisor, custom_agent],
        entry_point=orchestrator,
        ...
    )
    return swarm
```

### 3. Add Custom Tools

Create tools in `src/tools/custom_tools.py`:

```python
from strands import tool

@tool
def custom_search_tool(query: str) -> str:
    """Search the internal documentation for relevant information.

    Args:
        query: The search query string.
    Returns:
        Search results as formatted text.
    """
    return f"Results for: {query}"
```

---

## ❓ FAQ & Troubleshooting

### "Ollama connection refused"

**Docker:** Check `docker compose logs ollama`
**Local:** Ensure `ollama serve` is running: `curl http://localhost:11434/api/tags`

### "No module named 'strands'"

The `strands-agents` package isn't installed. Run:
```bash
pip install strands-agents>=0.1.0
```

(Note: `strands-agents[ollama]` does not exist — the `ollama` package is installed separately.)

### ChromaDB is slow on first query

ChromaDB loads its index into memory on first access. Subsequent queries are faster.

### "413 Request Entity Too Large"

Uploaded file exceeds the 50 MB limit. Increase `MAX_FILE_SIZE` in `backend/routes_rag.py`.

### "Token has expired"

JWT tokens expire after 24 hours. Log out and log back in.

### How do I reset everything?

```bash
# Docker: stop and delete all data
docker compose down -v

# Local: delete the data directory
rm -rf data/
```

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

Built with ❤️ using [Strands Agents SDK](https://strandsagents.com/), [FastAPI](https://fastapi.tiangolo.com/), [Jinja2](https://jinja.palletsprojects.com/), [Tailwind CSS](https://tailwindcss.com/), [ChromaDB](https://www.trychroma.com/), and [Ollama](https://ollama.ai/).
