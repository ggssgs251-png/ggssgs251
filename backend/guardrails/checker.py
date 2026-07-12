"""Guardrail checker — inspects messages against rules and returns pass/block results.

Monitored at the 'guardrail' stage.
"""

from dataclasses import dataclass, field
from typing import Any

from backend.logging_config import get_stage_logger

from .rules import (
    BLOCK_THRESHOLD,
    FLAGGED_CATEGORIES,
    HATE_SPEECH_PATTERNS,
    PROFANITY_PATTERNS,
    REGEX_PATTERNS,
)

logger = get_stage_logger("guardrail")


@dataclass
class GuardrailResult:
    """Result from a guardrail check.

    Attributes:
        passed: True if the message is allowed, False if blocked.
        score: Total weighted severity score.
        violations: List of violation descriptions.
        reason: User-facing explanation (only set when blocked).
    """
    passed: bool = True
    score: int = 0
    violations: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""


class GuardrailChecker:
    """Lightweight content guardrail that checks messages before they reach agents.

    Usage:
        checker = GuardrailChecker()
        result = checker.check("Hello, what is machine learning?")
        if result.passed:
            # forward to swarm
        else:
            # return result.reason to the user
    """

    def check(self, message: str) -> GuardrailResult:
        """Inspect a message and return the guardrail result.

        The checker evaluates:
        1. Regex patterns (PII: SSN, credit cards, emails, API keys, etc.)
        2. Word blocklists (profanity, hate speech)

        Each match adds a weighted score. If total score >= BLOCK_THRESHOLD,
        the message is blocked.
        """
        violations: list[dict[str, Any]] = []
        total_score = 0

        # ── 1. Check regex patterns ──
        for category, pattern in REGEX_PATTERNS.items():
            matches = pattern.findall(message)
            if matches:
                weight = FLAGGED_CATEGORIES.get(category, {}).get("weight", 5)
                reason = FLAGGED_CATEGORIES.get(category, {}).get(
                    "reason", f"Flagged content detected: {category}"
                )
                violation = {
                    "category": category,
                    "weight": weight,
                    "matches": list(set(matches))[:3],  # limit to 3 examples
                    "reason": reason,
                }
                violations.append(violation)
                total_score += weight * min(len(matches), 3)
                logger.debug(
                    "Guardrail match: category=%s, matches=%d, weight=%d",
                    category,
                    len(matches),
                    weight,
                )

        # ── 2. Check profanity blocklist ──
        for pattern in PROFANITY_PATTERNS:
            matches = pattern.findall(message)
            if matches:
                weight = FLAGGED_CATEGORIES["profanity"]["weight"]
                violation = {
                    "category": "profanity",
                    "weight": weight,
                    "matches": list(set(matches))[:3],
                    "reason": FLAGGED_CATEGORIES["profanity"]["reason"],
                }
                violations.append(violation)
                total_score += weight
                logger.debug("Guardrail match: profanity detected")

        # ── 3. Check hate speech blocklist ──
        for pattern in HATE_SPEECH_PATTERNS:
            matches = pattern.findall(message)
            if matches:
                weight = FLAGGED_CATEGORIES["hate_speech"]["weight"]
                violation = {
                    "category": "hate_speech",
                    "weight": weight,
                    "matches": list(set(matches))[:3],
                    "reason": FLAGGED_CATEGORIES["hate_speech"]["reason"],
                }
                violations.append(violation)
                total_score += weight
                logger.warning("Guardrail match: hate speech detected!")

        # ── 4. Deduplicate violations by category ──
        seen_categories = set()
        unique_violations = []
        for v in violations:
            if v["category"] not in seen_categories:
                seen_categories.add(v["category"])
                unique_violations.append(v)

        # ── 5. Determine result ──
        if total_score >= BLOCK_THRESHOLD:
            # Build a user-friendly reason
            reasons = [v["reason"] for v in unique_violations]
            primary_reason = reasons[0] if reasons else "Message was blocked by content filter."

            logger.warning(
                "BLOCKED | score=%d/%d | violations=%s",
                total_score,
                BLOCK_THRESHOLD,
                [v["category"] for v in unique_violations],
            )

            return GuardrailResult(
                passed=False,
                score=total_score,
                violations=unique_violations,
                reason=(
                    f"⚠️ **Content Warning**: {primary_reason} "
                    f"Please rephrase your message and try again. "
                    f"(Flagged categories: {', '.join(v['category'] for v in unique_violations)})"
                ),
            )

        # Passed — log any minor violations (below threshold)
        if unique_violations:
            logger.info(
                "Guardrail PASSED with minor flags | score=%d/%d | categories=%s",
                total_score,
                BLOCK_THRESHOLD,
                [v["category"] for v in unique_violations],
            )

        return GuardrailResult(passed=True, score=total_score, violations=unique_violations)


# Singleton for reuse
_checker: GuardrailChecker | None = None


def get_checker() -> GuardrailChecker:
    """Get or create the shared GuardrailChecker instance."""
    global _checker
    if _checker is None:
        _checker = GuardrailChecker()
    return _checker
