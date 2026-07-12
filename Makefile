# ──────────────────────────────────────────────────
# 🚀 ggssgs251 — Quick Commands
# ──────────────────────────────────────────────────

.PHONY: start dev test lint clean

# 🚀 Start everything (Ollama + Backend)
start:
	@bash scripts/start.sh

# 🐍 Start only the backend (assumes Ollama is already running)
dev:
	@uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# 🧪 Run guardrail tests
test:
	@python -m pytest backend/tests/test_guardrails.py -v

# 🔍 Run linter
lint:
	@ruff check backend/ src/

# 🧹 Clean up generated files
clean:
	@rm -rf data/ .venv/ __pycache__/ .pytest_cache/ .ruff_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned up"
