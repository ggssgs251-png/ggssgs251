"""Chat API route — connects the frontend to the Strands Swarm with RAG context."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from strands.models.ollama import OllamaModel

from backend.auth import get_current_user
from backend.models import User
from backend.rag_engine import build_rag_context, query_documents
from backend.schemas import ChatRequest, ChatResponse
from src.orchestrator import create_swarm, run_swarm

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Cache the swarm (reuse across requests to keep conversation state)
_swarm_cache: dict[str, Any] = {}


def _get_or_create_swarm():
    """Get or create the cached Swarm instance."""
    global _swarm_cache
    if "swarm" not in _swarm_cache:
        model = OllamaModel(
            host="http://localhost:11434",
            model_id="llama3.1",
            temperature=0.7,
        )
        _swarm_cache["swarm"] = create_swarm(model)
        _swarm_cache["model"] = model
    return _swarm_cache["swarm"]


@router.post("/message", response_model=ChatResponse)
def send_message(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Send a message to the AI assistant.

    The message is first augmented with relevant context from the knowledge base
    (if any documents have been indexed), then routed through the orchestrator
    Swarm to the most appropriate specialist agent.
    """
    try:
        message = body.message
        routing_path = []

        # 1. Retrieve RAG context if documents exist
        rag_results = query_documents(message)
        augmented_message = message
        if rag_results:
            context = build_rag_context(rag_results)
            augmented_message = (
                f"Context from knowledge base:\n{context}\n\n"
                f"User question: {message}\n\n"
                f"Please answer based on the context above when relevant, "
                f"and use your own knowledge to supplement."
            )

        # 2. Run through the Swarm
        swarm = _get_or_create_swarm()
        result = run_swarm(swarm, augmented_message)

        # 3. Extract reply from the result
        # The SwarmResult contains node results; get the final agent's output
        if hasattr(result, "results") and result.results:
            # Find the last completed node
            for node_id, node_result in result.results.items():
                if hasattr(node_result, "result") and hasattr(node_result.result, "text"):
                    reply = node_result.result.text
                    routing_path.append(node_id)
                    break
            else:
                reply = "I processed your request but couldn't generate a clear response."
        else:
            reply = str(result) if result else "No response generated."

        # 4. Build routing path
        if hasattr(result, "node_history") and result.node_history:
            routing_path = [n.node_id for n in result.node_history]
        elif hasattr(result, "results") and result.results:
            routing_path = list(result.results.keys())

        logger.info(
            f"User '{current_user.username}' → Chat | path: {' → '.join(routing_path)}"
        )

        # Determine which agent handled it
        final_agent = routing_path[-1] if routing_path else "orchestrator"

        return ChatResponse(
            reply=reply,
            agent=final_agent,
            routing_path=routing_path,
        )

    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing error: {str(e)}",
        )


@router.post("/reset")
def reset_conversation(current_user: User = Depends(get_current_user)):
    """Reset the conversation by clearing the cached swarm."""
    global _swarm_cache
    _swarm_cache = {}
    logger.info(f"User '{current_user.username}' reset the conversation")
    return {"message": "Conversation reset successfully"}
