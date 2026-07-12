#!/usr/bin/env bash
# ──────────────────────────────────────────────────────
# 🚀 ggssgs251 — Single-Command Start Script
# ──────────────────────────────────────────────────────
# Usage:
#   bash scripts/start.sh
#   # OR from project root:
#   make start
#
# This script:
#   1. Checks for Ollama (installs if missing — macOS/Linux)
#   2. Starts Ollama server if not running
#   3. Pulls required models (tinyllama, nomic-embed-text)
#   4. Activates the Python virtual environment
#   5. Starts the FastAPI server (serves both API + Web UI)
#   6. Opens http://localhost:8000 in your browser
#
# Prerequisites:
#   - Python 3.10+
#   - ~4 GB free RAM for Ollama
# ──────────────────────────────────────────────────────

set -e

# ── Colors ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo ""
echo -e "${BLUE}=========================================="
echo -e "  🚀 ggssgs251 — Starting Everything"
echo -e "==========================================${NC}"
echo ""

# ──────────────────────────────────────────────
# Step 1: Check / Install Ollama
# ──────────────────────────────────────────────
echo -e "${YELLOW}[1/4]🔍 Checking Ollama...${NC}"

if command -v ollama &> /dev/null; then
    echo -e "  ✅ Ollama found at: $(which ollama)"
else
    echo -e "  ${YELLOW}⚠️  Ollama not found. Installing...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  📦 Downloading for macOS..."
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  📦 Installing prerequisites (zstd)..."
        apt-get update -qq && apt-get install -y -qq zstd 2>/dev/null || " ";
        echo "  📦 Downloading Ollama for Linux..."
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo -e "  ${RED}❌ Please install Ollama manually: https://ollama.ai${NC}"
        echo "     Then re-run this script."
        exit 1
    fi
    echo -e "  ✅ Ollama installed!"
fi

# ──────────────────────────────────────────────
# Step 2: Start Ollama Server (if not running)
# ──────────────────────────────────────────────
echo -e "${YELLOW}[2/4]🔥 Starting Ollama server...${NC}"

if curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo -e "  ✅ Ollama server already running on port 11434"
else
    echo -e "  Starting Ollama in the background..."
    ollama serve &
    OLLAMA_PID=$!
    echo -e "  ⏳ Waiting for Ollama to be ready..."
    
    # Wait up to 30 seconds for Ollama to start
    for i in $(seq 1 30); do
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            echo -e "  ✅ Ollama server ready! (PID: $OLLAMA_PID)"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "  ${RED}❌ Ollama failed to start. Check: ollama serve${NC}"
            exit 1
        fi
        sleep 1
    done
fi

# ──────────────────────────────────────────────
# Step 3: Pull Required Models
# ──────────────────────────────────────────────
echo -e "${YELLOW}[3/4]📥 Pulling models...${NC}"

# Check and pull tinyllama
if ollama list 2>/dev/null | grep -q "tinyllama"; then
    echo -e "  ✅ tinyllama already downloaded"
else
    echo -e "  ⏳ Downloading tinyllama (~637 MB)..."
    ollama pull tinyllama
    echo -e "  ✅ tinyllama ready"
fi

# Check and pull nomic-embed-text
if ollama list 2>/dev/null | grep -q "nomic-embed-text"; then
    echo -e "  ✅ nomic-embed-text already downloaded"
else
    echo -e "  ⏳ Downloading nomic-embed-text (~270 MB)..."
    ollama pull nomic-embed-text
    echo -e "  ✅ nomic-embed-text ready"
fi

# ──────────────────────────────────────────────
# Step 4: Start the FastAPI Server
# ──────────────────────────────────────────────
echo -e "${YELLOW}[4/4]🐍 Starting backend server...${NC}"

# Activate virtual environment (create if missing)
if [ ! -d ".venv" ]; then
    echo -e "  ${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install/update dependencies
echo -e "  📦 Installing Python dependencies..."

# Install core deps explicitly (pyproject.toml install can fail on sentence-transformers)
pip install --quiet --upgrade pip setuptools wheel 2>&1 | tail -1
pip install --quiet \
    strands-agents>=0.1.0 \
    ollama>=0.6.0 \
    fastapi>=0.110.0 \
    uvicorn[standard]>=0.27.0 \
    python-multipart>=0.0.9 \
    chromadb>=0.5.0 \
    sqlalchemy>=2.0.0 \
    pyjwt>=2.8.0 \
    bcrypt>=4.1.0 \
    pypdf2>=3.0.0 \
    python-docx>=1.1.0 \
    pydantic>=2.0.0 \
    httpx>=0.27.0 \
    jinja2>=3.1.0 \
    aiofiles>=24.1.0 2>&1 | tail -3

echo -e "  ✅ Dependencies installed"

# Start the server
echo ""
echo -e "${GREEN}=========================================="
echo -e "  🎉 All systems ready!"
echo -e "==========================================${NC}"
echo ""
echo -e "  📂 Open:  ${BLUE}http://localhost:8000${NC}"
echo -e "  📄 API:   ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  🩺 Health: ${BLUE}http://localhost:8000/health${NC}"
echo -e ""
echo -e "  ${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Run the FastAPI server
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
