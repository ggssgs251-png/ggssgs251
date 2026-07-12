# 🛡️ Guardrail Agent

The **Guardrail Agent** is a lightweight content filter that inspects all user messages
before they reach the AI agents. It is NOT an LLM-based agent — it uses fast regex
pattern matching and blocklist checks to avoid latency and token waste.

## Architecture

```
User Message → GuardrailChecker.check()
                  │
                  ├─ ✅ PASS (score < 10) → Swarm (Orchestrator → Specialists)
                  │
                  └─ ❌ BLOCK (score ≥ 10) → HTTP 422 + violation details
```

## Detection Categories

| Category | Severity | Detection Method | Example |
|----------|----------|-----------------|---------|
| Hate Speech | 🔴 Critical (10) | Word blocklist | Racial slurs, hate group references |
| SSN | 🔴 Critical (9) | Regex | `123-45-6789` |
| Credit Card | 🔴 Critical (9) | Regex | `4111-1111-1111-1111` |
| API Key | 🔴 Critical (9) | Regex | `sk-proj-...`, `ghp_...` |
| Profanity | 🟠 High (8) | Word blocklist | Common swear words |
| Crypto Wallet | 🟠 High (7) | Regex | BTC/ETH addresses |
| Phone Number | 🟡 Medium (6) | Regex | `(555) 123-4567` |
| Password-like | 🟡 Medium (6) | Regex | `password: secret123` |
| Email | 🟡 Medium (5) | Regex | `user@example.com` |
| Personal Data | 🟡 Medium (5) | Regex | Identifying info patterns |
| IP Address | 🟢 Low (4) | Regex | `192.168.1.1` |

## Threshold

- **Block threshold**: Total weighted score ≥ **10**
- Each match adds `weight × count` to the score (capped at 3 matches per category)

## Location

- **Source code**: `backend/guardrails/`
- **Rules**: `backend/guardrails/rules.py`
- **Checker**: `backend/guardrails/checker.py`

## Testing

```bash
curl -X POST 'http://localhost:8000/guardrail/check?text=test+message'
```

## Customization

- Adjust `BLOCK_THRESHOLD` in `backend/guardrails/rules.py`
- Add words to `PROFANITY_BLOCKLIST` or `HATE_SPEECH_BLOCKLIST` lists
- Add new regex patterns to `REGEX_PATTERNS` dict
- Change category weight in `FLAGGED_CATEGORIES` dict
