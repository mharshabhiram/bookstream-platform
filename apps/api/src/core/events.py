"""
Application lifecycle events.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.core.config import settings
from src.core.logging import configure_logging, get_logger
from src.db.session import engine
from src.services.cache import cache_service
from src.services.storage import storage_service

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle."""
    # Startup
    configure_logging()
    logger.info(
        "application_startup",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
    )

    # Initialize services
    await cache_service.connect()
    await storage_service.initialize()

    yield

    # Shutdown
    logger.info("application_shutdown")
    await cache_service.disconnect()
    await engine.dispose()
