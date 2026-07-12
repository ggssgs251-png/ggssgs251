"""Guardrail rules: blocklists, regex patterns, and category definitions.

All lists are case-insensitive at check time. These are NOT exhaustive —
they serve as a strong first line of defense. For production use,
integrate with a dedicated PII/compliance service.
"""

import re
from typing import Final

# ──────────────────────────────────────────────
# Flagged Categories & Their Severity
# ──────────────────────────────────────────────
# Each category has:
#   weight   - how many "points" a match adds (higher = more severe)
#   reason   - user-facing explanation when blocked

FLAGGED_CATEGORIES: Final[dict[str, dict]] = {
    "profanity": {
        "weight": 8,
        "reason": "Message contains inappropriate or offensive language.",
    },
    "hate_speech": {
        "weight": 10,
        "reason": "Message contains hate speech or discriminatory language.",
    },
    "ssn": {
        "weight": 9,
        "reason": "Message appears to contain a Social Security Number. Please remove it.",
    },
    "credit_card": {
        "weight": 9,
        "reason": "Message appears to contain a credit card number. Please remove it.",
    },
    "phone": {
        "weight": 6,
        "reason": "Message contains a phone number. Remove it to protect privacy.",
    },
    "email": {
        "weight": 5,
        "reason": "Message contains an email address. Remove it to protect privacy.",
    },
    "api_key": {
        "weight": 9,
        "reason": "Message appears to contain an API key or secret token. Please remove it.",
    },
    "crypto_wallet": {
        "weight": 7,
        "reason": "Message appears to contain a cryptocurrency wallet address.",
    },
    "ip_address": {
        "weight": 4,
        "reason": "Message contains an IP address. Remove it to protect privacy.",
    },
    "password_like": {
        "weight": 6,
        "reason": "Message may contain a password or credential.",
    },
    "personal_data": {
        "weight": 5,
        "reason": "Message appears to contain personal identifying information.",
    },
}

# Threshold: total weighted score above this will block the message
BLOCK_THRESHOLD: Final[int] = 10


# ──────────────────────────────────────────────
# Regex Patterns
# ──────────────────────────────────────────────

REGEX_PATTERNS: Final[dict[str, re.Pattern]] = {
    # SSN: 123-45-6789 or 123456789
    "ssn": re.compile(
        r"\b(?!(000|666|9\d{2})-\d{2}-\d{4})(\d{3}-\d{2}-\d{4}|\d{9})\b"
    ),
    # Credit card: major card patterns (16 digits, Luhn not checked here)
    "credit_card": re.compile(
        r"\b(?:\d{4}[- ]?){3}\d{4}\b"
    ),
    # US Phone: (555) 123-4567, 555-123-4567, +1 555 123 4567
    "phone": re.compile(
        r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    ),
    # Email (basic pattern)
    "email": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    ),
    # API key / token patterns (common formats)
    "api_key": re.compile(
        r"\b(?:sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{36,}|"
        r"AIza[0-9A-Za-z_-]{35}|xox[baprs]-[0-9A-Za-z-]{10,}|"
        r"pk\.[A-Za-z0-9]{40,}|[A-Za-z0-9_-]{40,}={0,2})\b"
    ),
    # Crypto wallet addresses (BTC, ETH, etc.)
    "crypto_wallet": re.compile(
        r"\b(?:1[1-9A-HJ-NP-Za-km-z]{25,34}|"
        r"0x[a-fA-F0-9]{40}|"
        r"bc1[a-zA-HJ-NP-Z0-9]{25,39}|"
        r"r[1-9A-HJ-NP-Za-km-z]{25,34})\b"
    ),
    # IP address (IPv4)
    "ip_address": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
        r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    ),
    # Password-like: "password: xxx" or "pass: xxx"
    "password_like": re.compile(
        r"\b(?:password|passwd|pwd|secret)\s*[:=]\s*\S+\b",
        re.IGNORECASE,
    ),
    # Personal data patterns
    "personal_data": re.compile(
        r"\b\d{3}-?\d{2}-?\d{4}\b"  # Additional SSN catchall
    ),
}


# ──────────────────────────────────────────────
# Profanity / Hate Speech Blocklist
# ──────────────────────────────────────────────
# These are the most common words — a production system should use
# a proper content moderation API (e.g., Azure Content Safety, etc.)

PROFANITY_BLOCKLIST: Final[list[str]] = [
    "fuck",
    "fucking",
    "fucked",
    "fucker",
    "shit",
    "shits",
    "shitting",
    "asshole",
    "bastard",
    "bitch",
    "bitches",
    "bitching",
    "bullshit",
    "cock",
    "cocksucker",
    "cunt",
    "damn",
    "dammit",
    "dick",
    "dickhead",
    "douchebag",
    "goddamn",
    "goddamnit",
    "jackass",
    "motherfucker",
    "motherfucking",
    "nigga",
    "nigger",
    "piss",
    "pissed",
    "prick",
    "pussy",
    "slut",
    "son of a bitch",
    "twat",
    "whore",
    "wanker",
]

HATE_SPEECH_BLOCKLIST: Final[list[str]] = [
    "kill all",
    "exterminate",
    "white power",
    "heil hitler",
    "nazi",
    "white supremacy",
    "race traitor",
    "racial purity",
    "ethnic cleansing",
    "gas the",
]


# ──────────────────────────────────────────────
# Compiled word-boundary patterns
# ──────────────────────────────────────────────

def _compile_word_patterns(words: list[str]) -> list[re.Pattern]:
    """Compile a list of words into word-boundary regex patterns."""
    return [re.compile(rf"\b{re.escape(w)}\b", re.IGNORECASE) for w in words]


PROFANITY_PATTERNS: Final[list[re.Pattern]] = _compile_word_patterns(PROFANITY_BLOCKLIST)
HATE_SPEECH_PATTERNS: Final[list[re.Pattern]] = _compile_word_patterns(HATE_SPEECH_BLOCKLIST)
