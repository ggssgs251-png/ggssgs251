# ── Stage 1: Base / Dependencies ──
FROM python:3.11-slim AS builder

WORKDIR /install

# Install system build deps (for chromadb, pypdf2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml /app/pyproject.toml

# Install dependencies into a local directory
RUN pip install --no-cache-dir --prefix=/install \
    'strands-agents[ollama]>=0.1.0' \
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
    'httpx>=0.27.0' \
    'jinja2>=3.1.0' \
    'aiofiles>=24.1.0'


# ── Stage 2: Runtime ──
FROM python:3.11-slim

WORKDIR /app

# Install runtime system deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY backend/ /app/backend/
COPY src/ /app/src/
COPY pyproject.toml /app/

# Copy prompts (system prompts for agents)
COPY prompts/ /app/prompts/

# Create data directory (will be mounted as a volume)
RUN mkdir -p /app/data

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OLLAMA_HOST=http://ollama:11434
ENV OLLAMA_MODEL=llama3.1
ENV OLLAMA_EMBED_MODEL=nomic-embed-text
ENV CORS_ORIGINS=http://localhost:8000
ENV SECRET_KEY=change-me-in-production-use-a-real-secret

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
