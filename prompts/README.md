# 🤖 Agent Prompts

This directory contains the **system prompts** for each agent in the ggssgs251 multi-agent system. These prompts define the personality, capabilities, and behavior of each AI agent.

## 📂 Prompt Files

| File | Agent | Purpose |
|------|-------|---------|
| `orchestrator.md` | 🧠 Orchestrator | Routes user requests to the right specialist |
| `data_tutor.md` | 📊 Data Tutor | Data science, statistics, and analysis expert |
| `code_advisor.md` | 💻 Code Advisor | Programming and software engineering expert |
| `guardrail_agent.md` | 🛡️ Guardrail Agent | Content filtering and PII detection (system-level, not LLM) |

## ✏️ How to Edit

1. **Edit the `.md` file** for the agent whose behavior you want to change
2. **Changes take effect on next server restart** (prompts are loaded at startup)
3. **Keep the format consistent**: Use `##` headers for sections, `- **bold**` for capabilities

## 🔄 How It Works

The prompts are loaded by the Python code in `src/agents/` and `src/orchestrator.py`
at runtime. The loading logic reads `.md` files from this directory and passes
them as `system_prompt` to the `Agent()` constructor.

## 📝 Tips for Writing Good Prompts

- **Be specific**: Clearly define the agent's role, capabilities, and boundaries
- **Use examples**: Show the agent how to handle edge cases
- **Set tone**: Describe communication style (warm, precise, educational, etc.)
- **Define handoff rules**: When should the agent pass control to another agent?
- **Avoid contradictions**: Keep instructions consistent across all agents
