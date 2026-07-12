#!/usr/bin/env bash
# ──────────────────────────────────────────────────────
# Start Jupyter Notebook with the ggssgs251 kernel
# ──────────────────────────────────────────────────────
# Usage:
#   bash scripts/start_jupyter.sh
#
# This activates the project virtual environment and
# launches Jupyter Notebook, opening the notebooks/
# directory. Make sure the backend is already running
# before using the notebooks.
#
# Prerequisites:
#   - Backend running: uvicorn backend.app:app --reload --port 8000
#   - Ollama running:  ollama serve
# ──────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  🚀 ggssgs251 - Jupyter Notebook"
echo "=========================================="
echo ""
echo "📂 Project: $PROJECT_DIR"
echo "🔬 Kernel:  ggssgs251 (Python 3.10)"
echo ""
echo "⚠️  Make sure these are running BEFORE using the notebooks:"
echo "   1. Backend: uvicorn backend.app:app --reload --port 8000"
echo "   2. Ollama:  ollama serve  (with llama3.1 and nomic-embed-text)"
echo ""

# Activate venv
cd "$PROJECT_DIR"
source .venv/bin/activate

# Create sample data directory if needed
mkdir -p data/sample_docs

# Launch Jupyter
echo "📓 Opening notebooks/ directory..."
echo ""
jupyter notebook notebooks/ --ip=0.0.0.0 --port=8888 --no-browser
