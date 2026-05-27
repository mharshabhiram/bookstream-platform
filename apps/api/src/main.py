"""
BookStream FastAPI Application
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.logging import configure_logging, get_logger
from src.core.events import lifespan
from src.api.v1.endpoints import router as api_router
from src.exceptions.base import APIException

logger = get_logger(__name__)


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        description="Premium Ebook Reading Platform API",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ─── Middleware ───────────────────────────────────────────────

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page-Count"],
    )

    # Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Trusted hosts (production only)
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.bookstream.io", "bookstream.io"],
        )

    # ─── Exception Handlers ───────────────────────────────────────

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """Handle custom API exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(
            "unhandled_exception",
            error=str(exc),
            path=request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unexpected error occurred",
                "code": "ERR_INTERNAL",
                "details": {},
            },
        )

    # ─── Routes ───────────────────────────────────────────────────

    app.include_router(api_router, prefix="/api")

    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        return {"status": "healthy", "service": settings.APP_NAME}

    @app.get("/")
    async def root() -> dict:
        """API root."""
        return {
            "name": settings.APP_NAME,
            "version": "1.0.0",
            "docs": "/docs",
        }

    return app


app = create_application()
