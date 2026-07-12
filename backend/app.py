"""FastAPI application entry point.

Serves both the HTML frontend (Jinja2 templates) and REST API.
Run with: uvicorn backend.app:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

from backend.auth import router as auth_router
from backend.config import CORS_ORIGINS, DATA_DIR, UPLOAD_DIR
from backend.database import init_db
from backend.guardrails.checker import get_checker
from backend.logging_config import get_stage_logger, init_logging
from backend.routes_chat import router as chat_router
from backend.routes_rag import router as rag_router

# Initialize structured logging
init_logging()
logger = get_stage_logger("system")

# ── Setup templates and static files ──
BASE_DIR = Path(__file__).resolve().parent

# Create a Jinja2 environment without auto-reload caching issues
jinja_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    auto_reload=False,  # disable cache key issues in constrained envs
    enable_async=True,
)
templates = Jinja2Templates(env=jinja_env)
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: init DB on startup."""
    logger.info("Starting ggssgs251 API server...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down ggssgs251 API server...")


app = FastAPI(
    title="ggssgs251 — Multi-Agent AI System",
    description="RAG-powered multi-agent system with Data Tutor and Code Advisor",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Frontend Routes (Jinja2 Templates) ──

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


# ── API Routes ──

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/guardrail/check")
def check_guardrail(text: str = ""):
    """Test the guardrail agent against arbitrary text."""
    result = get_checker().check(text)
    return {
        "passed": result.passed,
        "score": result.score,
        "violations": result.violations,
        "blocked": not result.passed,
        "reason": result.reason if not result.passed else "",
    }


# Register REST API routers (all prefixed with /api via nginx proxy)
# The frontend JS calls /api/auth/*, /api/chat/*, /api/rag/*
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(rag_router, prefix="/api")


def run():
    """Convenience entry: python -m backend.app"""
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
