"""Swarm orchestrator that coordinates the multi-agent system.

Uses the Strands Swarm pattern to dynamically route user requests
to the appropriate specialist agent (Data Tutor or Code Advisor).
"""

from strands import Agent
from strands.models.ollama import OllamaModel
from strands.multiagent import Swarm, SwarmResult

from src.agents import create_code_advisor, create_data_tutor

ORCHESTRATOR_SYSTEM_PROMPT = """You are the **Orchestrator** — the intelligent router for a team of AI specialists.

## Your Team
1. **Data Tutor** — Expert in data science, statistics, and data analysis.
   Delegate: Data cleaning, visualization, statistical tests, ML concepts.
2. **Code Advisor** — Expert in software engineering and programming.
   Delegate: Code reviews, code explanations, debugging help, best practices.

## Your Role
- Listen to the user's request and determine which specialist can best help.
- If the request is clearly data/statistics-related → hand off to **Data Tutor**.
- If the request is clearly coding/programming-related → hand off to **Code Advisor**.
- If the request spans both areas, start with the most relevant specialist.
- If the request is general (greetings, simple questions), handle it yourself.

## Guidelines
- Always explain which specialist you're routing to and why.
- Be warm and helpful in your tone.
- Never fabricate specialist capabilities — stay within the defined roles.
- If a specialist can't fully resolve the request, they can hand back to you.
"""


def create_swarm(model: OllamaModel) -> Swarm:
    """Create the Swarm orchestrator with all specialist agents.

    The Swarm pattern enables agents to dynamically hand off tasks
    to each other based on the user's needs.

    Args:
        model: The Ollama model instance shared by all agents.

    Returns:
        A configured Swarm instance ready for invocation.
    """
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

    return swarm


def run_swarm(swarm: Swarm, task: str) -> SwarmResult:
    """Run the swarm with a given task.

    Args:
        swarm: The configured Swarm instance.
        task: The user's request or question.

    Returns:
        The result of the swarm execution.
    """
    return swarm(task)
