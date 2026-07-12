"""Data Tutor agent - helps users understand data and statistics.

Loads its system prompt from prompts/data_tutor.md.
"""

from pathlib import Path

from strands import Agent
from strands.models.ollama import OllamaModel

from src.tools import analyze_dataset_tool, explain_concept_tool


def _load_prompt() -> str:
    """Load the Data Tutor system prompt from the prompts directory."""
    prompt_path = Path(__file__).resolve().parent.parent.parent / "prompts" / "data_tutor.md"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    # Fallback if file doesn't exist
    return "You are the Data Tutor, an expert in data science, statistics, and data analysis."


DATA_TUTOR_SYSTEM_PROMPT = _load_prompt()


def create_data_tutor(model: OllamaModel) -> Agent:
    """Create and return a Data Tutor agent.

    Args:
        model: The Ollama model instance to power the agent.

    Returns:
        A configured Agent instance with data tutor capabilities.
    """
    return Agent(
        model=model,
        system_prompt=DATA_TUTOR_SYSTEM_PROMPT,
        tools=[analyze_dataset_tool, explain_concept_tool],
    )


def reload_prompt() -> None:
    """Reload the system prompt from file (call after editing prompts/data_tutor.md)."""
    global DATA_TUTOR_SYSTEM_PROMPT
    DATA_TUTOR_SYSTEM_PROMPT = _load_prompt()
