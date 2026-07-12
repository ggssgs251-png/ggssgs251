# 🤖 ggssgs251 — Multi-Agent AI System with RAG

An intelligent multi-agent AI system powered by the **Strands Agents SDK**, augmented with **RAG (Retrieval-Augmented Generation)** over your proprietary documents, complete with **user authentication** and a **modern web UI**.

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
| 🖥️ **Modern Web UI** | React 19 + Vite + shadcn/ui + Framer Motion animations |
| 🛡️ **100% Local & Private** | No cloud costs, no data leaves your machine |
| 🔄 **Dynamic Agent Routing** | Swarm pattern — agents dynamically hand off tasks |
| 📄 **Multi-format Upload** | PDF, Word (.docx), Plain Text (.txt), Markdown (.md) |
| 🔎 **Semantic Search** | ChromaDB vector search over your indexed documents |
| 🐳 **Dockerized** | One-command setup with Docker Compose |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Port 3000)                      │
│              React 19 + Vite + shadcn/ui + Framer Motion         │
│                                                                  │
│    Landing Page  →  Login/Register  →  Dashboard  →  Chat      │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP (REST API via /api/*)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend API (Port 8000)                      │
│                          FastAPI + Uvicorn                       │
│                                                                  │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  Auth   │  │  Chat    │  │   RAG    │  │ Knowledge Mgmt │  │
│  │ Routes  │  │ Routes   │  │  Routes  │  │    Routes      │  │
│  └────┬────┘  └────┬─────┘  └────┬─────┘  └───────┬────────┘  │
│       │            │             │                  │           │
│  ┌────▼────────────▼─────────────▼──────────────────▼───────┐  │
│  │                    Strands Swarm                         │  │
│  │  ┌────────────────┐  ┌────────────┐  ┌──────────────┐  │  │
│  │  │  Orchestrator  │  │ Data Tutor │  │ Code Advisor │  │  │
│  │  │  (Entry point) │  │  (Stats)   │  │ (Coding)     │  │  │
│  │  └────────────────┘  └────────────┘  └──────────────┘  │  │
│  └───────────────────────────┬─────────────────────────────┘  │
│                              │                                 │
│  ┌───────────────────────────┼─────────────────────────────┐  │
│  │       SQLite (users.db)   │     ChromaDB (vectors)     │  │
│  │       User accounts       │     Document embeddings    │  │
│  └───────────────────────────┴─────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌──────────────────────────────────┐
              │     Ollama (Port 11434)           │
              │  ┌──────────┐  ┌───────────────┐ │
              │  │ llama3.1 │  │ nomic-embed   │ │
              │  │  (LLM)   │  │  (embeddings) │ │
              │  └──────────┘  └───────────────┘ │
              └──────────────────────────────────┘
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

The fastest way to get everything running is with Docker Compose. This starts three services:

1. **Ollama** — LLM server (automatically pulls `llama3.1` and `nomic-embed-text`)
2. **Backend** — FastAPI + Strands Agents + ChromaDB
3. **Frontend** — Nginx serving the React SPA

### Prerequisites

- **Docker** (version 24+) and **Docker Compose** (version 2.20+)
  - [Install Docker Desktop](https://docs.docker.com/get-docker/) (includes Compose)
  - Or [Install Docker Engine + Compose plugin](https://docs.docker.com/engine/install/)
- **~8 GB free RAM** (for running local LLM in Docker)
- **~5 GB free disk space** (for Docker images and LLM models)

### Step 1: Clone & Configure

```bash
# Clone the repository
git clone https://github.com/ggssgs251-png/ggssgs251.git
cd ggssgs251

# (Optional) Set a secure secret key for JWT tokens
# On macOS/Linux:
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env

# On Windows (PowerShell):
# python -c "import secrets; print(secrets.token_hex(32))" | ForEach-Object { "SECRET_KEY=$_" | Out-File -FilePath .env }

# See .env.example for all available variables
```

### Step 2: Build & Start

```bash
# Build images and start all services
docker compose up --build

# Or run in detached mode (background)
docker compose up --build -d
```

### Step 3: Wait for Startup

The first startup takes **2-5 minutes** because:
- Docker images are being built (backend + frontend)
- Ollama downloads `llama3.1` (~4 GB) and `nomic-embed-text` (~270 MB)

Watch the logs to track progress:

```bash
# Watch all services
docker compose logs -f

# Watch just Ollama model downloads
docker compose logs -f ollama

# Watch the backend
docker compose logs -f backend
```

You'll see:
1. `ggssgs251-ollama` → "Models ready!"
2. `ggssgs251-backend` → "Database initialized" + health check passing
3. `ggssgs251-frontend` → ready immediately after backend

### Step 4: Open the App

```
http://localhost:3000
```

### Step 5: Create an Account

1. Click **"Get Started"** or navigate to **/register**
2. Enter your email, username, and password
3. You'll be auto-logged in and redirected to the Dashboard

### Docker Quick Commands

```bash
# Start all services (after initial build)
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Stop and delete volumes (wipes all data: users, documents, models!)
docker compose down -v

# Rebuild a specific service
docker compose build backend
docker compose build frontend

# Restart a specific service
docker compose restart backend

# Check service health
docker compose ps
```

### Common Docker Issues

| Problem | Solution |
|---------|----------|
| Port 3000 already in use | Change `"3000:3000"` to `"3001:3000"` in `docker-compose.yml` |
| Port 8000 already in use | Same approach for backend port |
| Ollama runs out of memory | Add `--memory=8g` to Docker resources, or use a smaller model |
| Backend can't reach Ollama | Check `OLLAMA_HOST=http://ollama:11434` in `docker-compose.yml` |
| Models need re-downloading | `docker compose down -v` clears `ollama_data` volume |

---

## 🛠️ Local Development Setup

If you prefer to run without Docker (e.g., for development), follow these steps.

### Prerequisites

- **Python 3.10+**
- **Node.js 20+** and **npm** (or **Bun**)
- **Ollama** — [install from ollama.ai](https://ollama.ai)

### Step 1: Install Ollama & Pull Models

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the LLM and embedding models
ollama pull llama3.1
ollama pull nomic-embed-text

# Start the Ollama server in a separate terminal
ollama serve
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
# Should return a JSON list of models
```

### Step 2: Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install Python dependencies
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
            'pydantic>=2.0.0' \
            'httpx>=0.27.0'

# Start the API server
uvicorn backend.app:app --reload --port 8000
```

Verify the backend is running:
```bash
curl http://localhost:8000/health
# Returns: {"status": "ok", "version": "0.1.0"}
```

### Step 3: Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies (use npm or bun)
npm install
# OR
bun install

# Start the Vite dev server
npm run dev
# OR
bun run dev
```

### Step 4: Open the App

```
http://localhost:5173
```

The Vite dev server proxies `/api/*` requests to `http://localhost:8000`.

### Step 5: Create an Account & Use the App

1. Register at `http://localhost:5173/register`
2. Upload documents on the Dashboard
3. Chat with agents at `http://localhost:5173/chat`

### Running Tests

```bash
# TypeScript type check (frontend)
cd frontend
npx tsc --noEmit

# Python (if you add tests)
cd backend
python -m pytest
```

---

## 📡 API Endpoints

All API endpoints are prefixed with `/api` when accessed from the frontend (proxied by Vite in dev, or Nginx in Docker).

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/register` | No | Register a new user |
| `POST` | `/auth/login` | No | Login, returns JWT token |
| `GET` | `/auth/me` | Yes | Get current user profile |
| `POST` | `/chat/message` | Yes | Send message to AI agents with RAG |
| `POST` | `/chat/reset` | Yes | Reset conversation history |
| `POST` | `/rag/upload` | Yes | Upload & index a document |
| `POST` | `/rag/query` | Yes | Search the knowledge base |
| `GET` | `/rag/documents` | Yes | List all indexed documents |
| `DELETE` | `/rag/documents/{filename}` | Yes | Delete a document from the index |
| `GET` | `/health` | No | Health check |

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
# Returns: {"access_token": "eyJ...", "token_type": "bearer"}

# 3. Chat with agents (using the token)
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
| **frontend** | `ggssgs251-frontend` | Custom (Nginx) | 3000 | 3000 | backend (healthy) |

### Volumes

| Volume | Mount Point | Purpose |
|--------|------------|---------|
| `ggssgs251_ollama_data` | `/root/.ollama` | Persists LLM models across restarts |
| `ggssgs251_backend_data` | `/app/data` | Persists SQLite DB, ChromaDB vectors, uploaded files |

### Network

All services are on a shared bridge network `ggssgs251-net` and can reach each other by container name:
- Backend → `http://ollama:11434`
- Frontend → `http://backend:8000` (via Nginx proxy)

### Dockerfiles

#### `backend/Dockerfile` — Multi-stage Python Build

| Stage | Base Image | Purpose |
|-------|-----------|---------|
| `builder` | `python:3.11-slim` | Installs all Python dependencies with build tools |
| `runtime` | `python:3.11-slim` | Copies only the installed packages + app code (~200 MB) |

The builder stage installs system packages (`gcc`, `g++`, `build-essential`) needed to compile native extensions for chromadb. The runtime stage only contains `curl` for health checks.

#### `frontend/Dockerfile` — Multi-stage Node + Nginx Build

| Stage | Base Image | Purpose |
|-------|-----------|---------|
| `builder` | `node:20-alpine` | Installs npm deps, runs TypeScript + Vite build |
| `runtime` | `nginx:alpine` | Copies `dist/` folder + nginx config (~5 MB static files) |

### Nginx Configuration

The `frontend/nginx.conf`:

- **`/api/`** — Proxies to `http://backend:8000` with `/api` prefix stripped
- **`/`** — Serves the SPA with `try_files` fallback to `index.html`
- **`/assets/`** — Long-lived cache for built assets (1 year)
- **Gzip** — Compresses text responses
- **Timeouts** — 300s read timeout for long-running agent tasks

### Environment Variables

See `.env.example` for all configurable variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-me-in-production...` | JWT signing secret (REQUIRED to change in production) |
| `OLLAMA_HOST` | `http://ollama:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1` | LLM model for agent responses |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Model for generating document embeddings |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Allowed CORS origins |

---

## 🔧 Configuration

### Changing the LLM Model

Edit the `OLLAMA_MODEL` environment variable:

**Docker:** Edit `docker-compose.yml` or `.env`:
```yaml
environment:
  - OLLAMA_MODEL=mistral
  # or: llama3.2, qwen2.5, deepseek-r1, etc.
```

**Local dev:** Edit `backend/config.py`:
```python
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
```

You'll also need to pull the model:
```bash
ollama pull mistral
```

### Changing the Embedding Model

For RAG embeddings, a small model like `nomic-embed-text` (270 MB) is recommended:
```bash
ollama pull nomic-embed-text
```

### Adjusting RAG Parameters

Edit `backend/config.py`:

```python
CHUNK_SIZE = 500          # Characters per document chunk
CHUNK_OVERLAP = 50        # Overlap between consecutive chunks
DEFAULT_RAG_RESULTS = 5   # Number of chunks to retrieve per query
RAG_MIN_SCORE = 0.3       # Minimum similarity score (0-1)
```

---

## 🗂️ Complete Project Structure

```
ggssgs251/
│
├── docker-compose.yml           # Docker Compose — 3 services
├── .env.example                 # Environment variable template
├── .dockerignore                # Root build context ignores
│
├── backend/
│   ├── Dockerfile               # Multi-stage Python build
│   ├── .dockerignore
│   ├── app.py                   # FastAPI entry point, CORS, lifespan
│   ├── config.py                # All configuration settings
│   ├── database.py              # SQLAlchemy + SQLite setup
│   ├── models.py                # User SQLAlchemy model
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── auth.py                  # JWT auth, bcrypt, /auth/* routes
│   ├── rag_engine.py            # ChromaDB RAG pipeline (index + search)
│   ├── routes_chat.py           # /chat/* endpoints with agent integration
│   └── routes_rag.py            # /rag/* endpoints for document management
│
├── frontend/
│   ├── Dockerfile               # Multi-stage Node → Nginx build
│   ├── nginx.conf               # Production Nginx config
│   ├── .dockerignore
│   ├── package.json             # React 19 + Vite + shadcn/ui deps
│   ├── vite.config.ts           # Vite config with /api proxy
│   ├── tsconfig*.json           # TypeScript configuration
│   ├── tailwind.config.ts       # Tailwind with custom theme
│   ├── postcss.config.js
│   ├── index.html               # HTML entry point
│   └── src/
│       ├── main.tsx             # React entry with Router + AuthProvider
│       ├── App.tsx              # Route definitions (public/protected)
│       ├── index.css            # Global CSS + Tailwind + theme variables
│       ├── lib/
│       │   ├── api.ts           # Full API client (auth, chat, RAG)
│       │   ├── auth-context.tsx  # React auth context provider
│       │   └── utils.ts         # cn() utility for class merging
│       └── pages/
│           ├── LandingPage.tsx   # Hero, features, CTA
│           ├── LoginPage.tsx     # Login form with JWT
│           ├── RegisterPage.tsx  # Registration with auto-login
│           ├── DashboardPage.tsx # Document upload, agent cards, management
│           └── ChatPage.tsx      # Chat UI, agent routing, sidebar RAG
│
├── src/                          # Python agent code (shared with backend)
│   ├── main.py                  # CLI entry point (npm alternative)
│   ├── orchestrator.py          # Strands Swarm setup + orchestration
│   ├── agents/
│   │   ├── data_tutor.py        # Data Tutor agent system prompt + tools
│   │   └── code_advisor.py      # Code Advisor agent system prompt + tools
│   └── tools/
│       └── custom_tools.py      # @tool-decorated functions
│
├── data/                        # Auto-created at runtime (gitignored)
│   ├── uploads/                 # Uploaded documents
│   ├── chroma_db/               # ChromaDB persistent storage
│   └── ggssgs251.db             # SQLite user database
│
├── pyproject.toml               # Python package + dependencies
├── README.md                    # This file
├── LICENSE                      # MIT License
└── .gitignore
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
Hand off to other agents when appropriate.
"""

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
        nodes=[orchestrator, data_tutor, code_advisor, custom_agent],  # 👈 Add here
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
    # Your tool implementation here
    return f"Results for: {query}"
```

---

## ❓ FAQ & Troubleshooting

### "Ollama connection refused"

**Docker:** Ensure the `ollama` service is healthy: `docker compose logs ollama`
**Local:** Ensure `ollama serve` is running: `curl http://localhost:11434/api/tags`

### "No module named 'strands'"

The `strands-agents[ollama]` package isn't installed. Run:
```bash
pip install 'strands-agents[ollama]'
```

### ChromaDB is slow on first query

ChromaDB loads its index into memory on first access. Subsequent queries are faster.

### "413 Request Entity Too Large"

Uploaded file exceeds the 50 MB limit. Reduce file size or increase `MAX_FILE_SIZE` in `backend/routes_rag.py`.

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

Built with ❤️ using [Strands Agents SDK](https://strandsagents.com/), [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), [shadcn/ui](https://ui.shadcn.com/), [ChromaDB](https://www.trychroma.com/), and [Ollama](https://ollama.ai/).
