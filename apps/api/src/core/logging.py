"""
Structured logging configuration for BookStream.
"""

import sys
import logging
from typing import Any

import structlog

from src.core.config import settings


def configure_logging() -> None:
    """Configure structured logging for the application."""

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ExtraAdder(),
    ]

    if settings.is_production:
        # Production: JSON format for log aggregation
        shared_processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ])
    else:
        # Development: Pretty console output
        shared_processors.extend([
            structlog.dev.ConsoleRenderer(
                colors=True,
                sort_keys=False,
            ),
        ])

    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if settings.APP_DEBUG else logging.INFO,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
