"""
BookStream Application Settings
Production-grade configuration with environment-based overrides.
"""

from functools import lru_cache
from typing import Any, Literal

from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ─────────────────────────────────────────────
    APP_NAME: str = "BookStream"
    APP_ENV: Literal["development", "staging", "production", "testing"] = "development"
    APP_DEBUG: bool = False
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"
    API_VERSION: str = "v1"

    # ─── Database ────────────────────────────────────────────────
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_RECYCLE: int = 1800
    DATABASE_ECHO: bool = False

    # ─── Redis ───────────────────────────────────────────────────
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    REDIS_CACHE_URL: RedisDsn = "redis://localhost:6379/1"

    # ─── JWT Authentication ──────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── OAuth Providers ─────────────────────────────────────────
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None

    # ─── Storage ─────────────────────────────────────────────────
    STORAGE_TYPE: Literal["local", "s3", "r2"] = "local"
    STORAGE_BUCKET: str = "bookstream-uploads"
    STORAGE_REGION: str = "us-east-1"
    STORAGE_ENDPOINT: str | None = None
    STORAGE_ACCESS_KEY: str | None = None
    STORAGE_SECRET_KEY: str | None = None
    STORAGE_PUBLIC_URL: str | None = None

    # ─── Email ───────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str = "noreply@bookstream.io"
    SMTP_TLS: bool = True

    # ─── Celery ──────────────────────────────────────────────────
    CELERY_BROKER_URL: RedisDsn = "redis://localhost:6379/2"
    CELERY_RESULT_BACKEND: RedisDsn = "redis://localhost:6379/3"

    # ─── Security ────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_UPLOAD_EXTENSIONS: set[str] = {
        ".epub", ".pdf", ".mobi", ".azw3", ".txt"
    }

    # ─── Pagination ──────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ─── Features ────────────────────────────────────────────────
    ENABLE_ANALYTICS: bool = True
    ENABLE_NOTIFICATIONS: bool = True
    ENABLE_SOCIAL: bool = True
    ENABLE_OFFLINE: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, list):
            return v
        return [str(v)]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in test environment."""
        return self.APP_ENV == "testing"

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return str(self.DATABASE_URL).replace("+asyncpg", "+psycopg2")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
