# 🤖 ggssgs251 — Multi-Agent AI System

An intelligent multi-agent system powered by the **Strands Agents SDK** with:
- **🧠 Orchestrator** — Routes your requests to the right specialist
- **📊 Data Tutor** — Expert in data science, statistics, and analysis
- **💻 Code Advisor** — Expert in programming and software best practices

Built with the **Swarm** orchestration pattern — agents dynamically hand off
tasks to each other based on your needs. Runs locally using **Ollama** for
completely free, private AI.

---

## 🚀 Quick Start

### 1. Install Ollama

Download from [ollama.ai](https://ollama.ai) or use Docker:

```bash
# Native install
curl -fsSL https://ollama.ai/install.sh | sh

# Or Docker
docker pull ollama/ollama
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### 2. Pull a model

```bash
ollama pull llama3.1
# Or try: ollama pull mistral, ollama pull qwen2.5, etc.
```

### 3. Start the Ollama server

```bash
ollama serve
```

### 4. Set up this project

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install 'strands-agents[ollama]' strands-agents-tools
```

### 5. Run the app

```bash
python -m src.main
```

---

## 🎮 Usage

Type your questions naturally and the orchestrator routes them to the right
specialist.

### Examples

```
🧑 You: Can you explain what a p-value is in statistics?
→ Routes to **Data Tutor**

🧑 You: Review this Python function for me...
→ Routes to **Code Advisor**

🧑 You: I have a CSV with sales data, how should I clean it?
→ Routes to **Data Tutor**

🧑 You: What's the best way to optimize this SQL query?
→ Routes to **Code Advisor**
```

### Commands

| Command | Description |
|---------|-------------|
| `/quit` | Exit the application |
| `/model <name>` | Switch to a different Ollama model at runtime |

---

## 🧠 Architecture

```
                    ┌──────────────┐
                    │  User Input   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Orchestrator  │  ← Entry point
                    │  (Swarm)     │     Routes to specialists
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
     ┌────────▼───┐  ┌────▼────┐
     │ Data Tutor  │  │  Code   │
     │             │  │ Advisor │
     └─────────────┘  └─────────┘
```

The **Swarm** pattern enables dynamic hand-offs:
1. Orchestrator receives the request
2. Determines which specialist is best suited
3. Hands off control to that agent
4. The specialist can complete the task or hand back to the orchestrator
5. Agents share context throughout the conversation

---

## 🛠️ Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Run in development mode
python -m src.main

# Or install as a package
pip install -e .
ggssgs251
```

### Customizing Models

Edit `src/main.py` to change the default model:

```python
ollama_model_id = "mistral"  # or "qwen2.5", "llama3.1", etc.
```

### Adding New Tools

Create tools in `src/tools/custom_tools.py` using the `@tool` decorator:

```python
from strands import tool

@tool
def my_new_tool(param: str) -> str:
    """Description for the LLM to understand when to use this tool."""
    return f"Result: {param}"
```

Then add them to the appropriate agent's `tools` list.

---

## 📋 Requirements

- **Python 3.10+**
- **Ollama** (local) or alternative LLM provider
- ~4-8GB RAM (for local LLM)

## 📄 License

MIT
