"""Guardrail Agent — lightweight content filtering and PII detection.

Architecture:
  User Message → GuardrailChecker.check() → Pass → Swarm
                                           → Block → HTTP 422 with reason

The guardrail runs BEFORE any LLM calls to avoid wasting tokens on
blocked content. It uses fast regex + blocklist matching, not an LLM.
"""

from .checker import GuardrailChecker, GuardrailResult
from .rules import FLAGGED_CATEGORIES

__all__ = [
    "FLAGGED_CATEGORIES",
    "GuardrailChecker",
    "GuardrailResult",
]
