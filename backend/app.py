"""FastAPI application entry point.

Run with: uvicorn backend.app:app --reload
Or:        python -m backend.app

Uses structured stage-level logging for monitoring each pipeline stage.
Stages: auth, guardrail, rag, chat, swarm, api.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# CORS — allow the frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}


# ── Guardrail test endpoint ──
@app.post("/guardrail/check")
def check_guardrail(text: str = ""):
    """Test the guardrail agent against arbitrary text.

    Use this endpoint to verify the guardrail is working during setup.
    Example: curl -X POST 'http://localhost:8000/guardrail/check?text=test%20message'
    """
    result = get_checker().check(text)
    return {
        "passed": result.passed,
        "score": result.score,
        "violations": result.violations,
        "blocked": not result.passed,
        "reason": result.reason if not result.passed else "",
    }


app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(rag_router)


def run():
    """Convenience entry: python -m backend.app"""
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
