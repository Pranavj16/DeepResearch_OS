"""Structured application logging configuration and context helpers."""

import sys
from pathlib import Path
from typing import Any

from loguru import logger

from app.core.settings import Settings, get_settings


def setup_logging(config: Settings | None = None) -> None:
    """Configure console and rotating file sinks from typed settings."""

    resolved_settings = config or get_settings()

    logger.remove()

    logger.add(
        sys.stdout,
        level=resolved_settings.LOG_LEVEL,
        format=resolved_settings.LOG_FORMAT,
        colorize=not resolved_settings.LOG_SERIALIZE,
        backtrace=resolved_settings.DEBUG,
        diagnose=resolved_settings.DEBUG,
        serialize=resolved_settings.LOG_SERIALIZE,
    )

    try:
        log_path = Path(resolved_settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_path,
            level=resolved_settings.LOG_LEVEL,
            rotation=resolved_settings.LOG_ROTATION,
            retention=resolved_settings.LOG_RETENTION,
            compression="zip",
            enqueue=True,
            backtrace=False,
            diagnose=False,
            serialize=resolved_settings.LOG_SERIALIZE,
        )
    except OSError:
        pass


def get_logger(**context: Any):
    """Return a logger bound to correlation and execution context fields."""

    return logger.bind(**context) if context else logger


def bind_context(**context: Any) -> None:
    """Bind contextual attributes to current logger context."""

    logger.configure(extra=context)


def clear_context() -> None:
    """Clear contextual attributes from logger."""

    logger.configure(extra={})


__all__ = ["bind_context", "clear_context", "get_logger", "setup_logging"]
