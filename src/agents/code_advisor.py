"""Code Advisor agent - helps users write, review, and understand code.

Loads its system prompt from prompts/code_advisor.md.
"""

from pathlib import Path

from strands import Agent
from strands.models.ollama import OllamaModel

from src.tools import review_code_tool, explain_code_tool


def _load_prompt() -> str:
    """Load the Code Advisor system prompt from the prompts directory."""
    prompt_path = Path(__file__).resolve().parent.parent.parent / "prompts" / "code_advisor.md"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    # Fallback if file doesn't exist
    return "You are the Code Advisor, an expert in software engineering and programming."


CODE_ADVISOR_SYSTEM_PROMPT = _load_prompt()


def create_code_advisor(model: OllamaModel) -> Agent:
    """Create and return a Code Advisor agent.

    Args:
        model: The Ollama model instance to power the agent.

    Returns:
        A configured Agent instance with code advisor capabilities.
    """
    return Agent(
        model=model,
        system_prompt=CODE_ADVISOR_SYSTEM_PROMPT,
        tools=[review_code_tool, explain_code_tool],
    )


def reload_prompt() -> None:
    """Reload the system prompt from file (call after editing prompts/code_advisor.md)."""
    global CODE_ADVISOR_SYSTEM_PROMPT
    CODE_ADVISOR_SYSTEM_PROMPT = _load_prompt()
