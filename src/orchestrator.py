"""Swarm orchestrator that coordinates the multi-agent system.

Uses the Strands Swarm pattern to dynamically route user requests
to the appropriate specialist agent (Data Tutor or Code Advisor).
Loads the orchestrator system prompt from prompts/orchestrator.md.
"""

import logging
from pathlib import Path
from time import time

from strands import Agent
from strands.models.ollama import OllamaModel
from strands.multiagent import Swarm, SwarmResult

from src.agents import create_code_advisor, create_data_tutor

logger = logging.getLogger(__name__)


def _load_prompt() -> str:
    """Load the Orchestrator system prompt from the prompts directory."""
    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "orchestrator.md"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    # Fallback if file doesn't exist
    return "You are the Orchestrator, the intelligent router for a team of AI specialists."


ORCHESTRATOR_SYSTEM_PROMPT = _load_prompt()


def create_swarm(model: OllamaModel) -> Swarm:
    """Create the Swarm orchestrator with all specialist agents.

    The Swarm pattern enables agents to dynamically hand off tasks
    to each other based on the user's needs.

    Args:
        model: The Ollama model instance shared by all agents.

    Returns:
        A configured Swarm instance ready for invocation.
    """
    t0 = time()

    # Create specialist agents
    data_tutor = create_data_tutor(model)
    code_advisor = create_code_advisor(model)

    # Create the orchestrator agent (entry point)
    orchestrator = Agent(
        model=model,
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
    )

    # Create the Swarm — agents self-organize and hand off dynamically
    swarm = Swarm(
        nodes=[orchestrator, data_tutor, code_advisor],
        entry_point=orchestrator,
        max_handoffs=20,
        max_iterations=20,
        execution_timeout=900.0,
        node_timeout=300.0,
        id="ggssgs251-swarm",
    )

    logger.info(
        "Swarm created with 3 agents (orchestrator, data_tutor, code_advisor) in %.2fs",
        time() - t0,
    )

    return swarm


def run_swarm(swarm: Swarm, task: str) -> SwarmResult:
    """Run the swarm with a given task.

    Args:
        swarm: The configured Swarm instance.
        task: The user's request or question.

    Returns:
        The result of the swarm execution.
    """
    logger.debug("Swarm invoked with task: %.80s...", task)
    t0 = time()
    result = swarm(task)
    elapsed = time() - t0
    logger.info("Swarm completed in %.2fs | status=%s", elapsed, result.status.value)
    return result


def reload_prompt() -> None:
    """Reload the orchestrator system prompt from file."""
    global ORCHESTRATOR_SYSTEM_PROMPT
    ORCHESTRATOR_SYSTEM_PROMPT = _load_prompt()
    logger.info("Orchestrator prompt reloaded from prompts/orchestrator.md")
