"""Tests for the Guardrail Agent.

All tests run without Ollama — they test pure Python regex + blocklist matching.
Scoring: threshold = 10. Items with weight < 10 alone will PASS (flagged but not blocked).
"""

# ruff: noqa: E402 — sys.path setup before application imports is intentional

import sys
from pathlib import Path

# Ensure the data/logs directory exists before importing the guardrail
_log_dir = Path(__file__).resolve().parent.parent.parent / "data" / "logs"
_log_dir.mkdir(parents=True, exist_ok=True)

# Ensure the project root is on sys.path
_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from backend.guardrails.checker import GuardrailChecker


def test_safe_inputs_pass():
    checker = GuardrailChecker()
    for msg in [
        "What is machine learning?",
        "Can you explain p-values?",
        "Review this Python function: def foo(): pass",
        "How do I clean a CSV with missing values?",
        "Hello, how are you today?",
        "Explain gradient descent to me",
    ]:
        assert checker.check(msg).passed, "Safe message should PASS"


def test_ssn_detection():
    """SSN (weight=9) alone should be flagged but PASS since 9 < 10."""
    checker = GuardrailChecker()
    result = checker.check("My SSN is 123-45-6789")
    categories = [v["category"] for v in result.violations]
    assert "ssn" in categories


def test_ssn_plus_email_blocks():
    """SSN (9) + email (5) = 14 >= 10, should BLOCK."""
    checker = GuardrailChecker()
    result = checker.check("My SSN is 123-45-6789 and email is user@example.com")
    assert not result.passed


def test_profanity_blocks():
    """Profanity (weight=8 per match, multiple matches exceed 10)."""
    checker = GuardrailChecker()
    result = checker.check("This is fucking shit")
    assert not result.passed
    cats = [v["category"] for v in result.violations]
    assert "profanity" in cats


def test_hate_speech_blocks():
    """Hate speech (weight=10) equals threshold."""
    checker = GuardrailChecker()
    result = checker.check("kill all people")
    assert not result.passed
    cats = [v["category"] for v in result.violations]
    assert "hate_speech" in cats


def test_phone_passes_alone():
    """Phone (weight=6) alone passes."""
    checker = GuardrailChecker()
    assert checker.check("Call me at (555) 123-4567").passed


def test_pii_combo_blocks():
    """Multiple PII items together block."""
    checker = GuardrailChecker()
    result = checker.check("My SSN is 123-45-6789 and card is 4111-1111-1111-1111")
    assert not result.passed


def test_safe_long_message():
    checker = GuardrailChecker()
    assert checker.check("Hello world. " * 500).passed


def test_unicode_safe():
    checker = GuardrailChecker()
    assert checker.check("héllo wörld 日本語").passed


def test_empty_passes():
    checker = GuardrailChecker()
    assert checker.check("a").passed
    assert checker.check("  ").passed


def test_block_threshold():
    from backend.guardrails.rules import BLOCK_THRESHOLD
    assert BLOCK_THRESHOLD == 10
