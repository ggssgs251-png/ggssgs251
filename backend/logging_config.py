"""Structured logging for monitoring each stage of the application pipeline.

Provides stage-specific loggers with consistent formatting, making it easy to
monitor, filter, and alert on each processing stage.

## Stages

| Logger Name | Stage | What It Logs |
|-------------|-------|--------------|
| stage.auth | 🔐 Auth | Registrations, logins, token validation |
| stage.guardrail | 🛡️ Guardrail | Content filtering, PII detection, blocks |
| stage.rag | 📚 RAG | Document indexing, embedding, retrieval |
| stage.chat | 💬 Chat | User messages, agent routing, responses |
| stage.swarm | 🧠 Swarm | Agent handoffs, execution path |
| stage.api | 🌐 API | Request/response metrics |
"""

import logging
import logging.config
import sys
from datetime import datetime, timezone
from typing import Any

# ──────────────────────────────────────────────
# Custom Formatter — adds stage, emoji, timing
# ──────────────────────────────────────────────

STAGE_EMOJIS = {
    "auth": "🔐",
    "guardrail": "🛡️",
    "rag": "📚",
    "chat": "💬",
    "swarm": "🧠",
    "api": "🌐",
    "system": "⚙️",
}


class StageFormatter(logging.Formatter):
    """Custom formatter that adds stage info and structured context."""

    def format(self, record: logging.LogRecord) -> str:
        # Determine stage name from logger name
        logger_name = record.name
        stage = logger_name.split(".")[-1] if logger_name.startswith("stage") else "system"
        emoji = STAGE_EMOJIS.get(stage, "📋")

        # Build the log message with stage prefix
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        level = record.levelname
        message = record.getMessage()

        # Add extra context if available
        extra = ""
        if hasattr(record, "user"):
            extra += f" [user={record.user}]"
        if hasattr(record, "duration_ms"):
            extra += f" [dur={record.duration_ms}ms]"
        if hasattr(record, "status"):
            extra += f" [status={record.status}]"
        if hasattr(record, "score"):
            extra += f" [score={record.score}]"

        return f"{emoji} [{stage:10s}] {level:<8s} | {message}{extra}"


# ──────────────────────────────────────────────
# Logging Configuration
# ──────────────────────────────────────────────

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "stage": {
            "()": StageFormatter,
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "format": '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "stage",
            "stream": sys.stdout,
        },
        "file_stages": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "data/logs/stages.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
        },
        "file_json": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "data/logs/stages.jsonl",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 3,
        },
        "file_errors": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "formatter": "detailed",
            "filename": "data/logs/errors.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 3,
        },
    },
    "loggers": {
        # Stage-specific loggers
        "stage.auth": {
            "level": "INFO",
            "handlers": ["console", "file_stages", "file_json"],
            "propagate": False,
        },
        "stage.guardrail": {
            "level": "INFO",
            "handlers": ["console", "file_stages", "file_json"],
            "propagate": False,
        },
        "stage.rag": {
            "level": "INFO",
            "handlers": ["console", "file_stages", "file_json"],
            "propagate": False,
        },
        "stage.chat": {
            "level": "INFO",
            "handlers": ["console", "file_stages", "file_json"],
            "propagate": False,
        },
        "stage.swarm": {
            "level": "INFO",
            "handlers": ["console", "file_stages", "file_json"],
            "propagate": False,
        },
        "stage.api": {
            "level": "INFO",
            "handlers": ["console", "file_stages", "file_json"],
            "propagate": False,
        },
        # Error logger (catches WARNING+ from all stage loggers)
        "errors": {
            "level": "WARNING",
            "handlers": ["file_errors", "console"],
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}


# ──────────────────────────────────────────────
# Stage Logger Factory
# ──────────────────────────────────────────────

_stage_loggers: dict[str, logging.Logger] = {}


def get_stage_logger(stage: str) -> logging.Logger:
    """Get or create a stage-specific logger with structured logging support.

    Args:
        stage: The stage name ('auth', 'guardrail', 'rag', 'chat', 'swarm', 'api')

    Returns:
        A configured logger that supports extra context fields.
    """
    logger_name = f"stage.{stage}"
    if logger_name not in _stage_loggers:
        logger = logging.getLogger(logger_name)
        _stage_loggers[logger_name] = logger
    return _stage_loggers[logger_name]


def init_logging() -> None:
    """Initialize the logging configuration.

    Call this once at application startup (in app.py lifespan).
    """
    import os
    from pathlib import Path

    # Ensure logs directory exists
    logs_dir = Path("data/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(LOGGING_CONFIG)

    stage = get_stage_logger("system")
    stage.info("Logging initialized — logs written to data/logs/")


# ──────────────────────────────────────────────
# Convenience: log helper with context
# ──────────────────────────────────────────────

def log_stage_event(
    stage: str,
    level: str,
    message: str,
    **context: Any,
) -> None:
    """Log a structured event for a specific stage with extra context.

    Args:
        stage: The stage name
        level: Log level ('info', 'warning', 'error', 'debug')
        message: The log message
        **context: Extra context fields (user, duration_ms, status, score, etc.)
    """
    logger = get_stage_logger(stage)
    log_method = getattr(logger, level, logger.info)

    # Create a LogRecord with extra context
    extra = logging.LogRecord(
        name=logger.name,
        level=logging.getLevelName(level.upper()),
        pathname="",
        lineno=0,
        msg=message,
        args=(),
        exc_info=None,
    )
    for key, value in context.items():
        setattr(extra, key, value)

    logger.handle(extra)
