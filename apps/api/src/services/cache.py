"""
Redis caching service.
"""

import json
from typing import Any

import redis.asyncio as redis

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Redis cache service with prefix support."""

    def __init__(self):
        self._redis: redis.Redis | None = None
        self.default_ttl = 3600  # 1 hour

    async def connect(self) -> None:
        """Connect to Redis."""
        self._redis = redis.from_url(
            str(settings.REDIS_CACHE_URL),
            decode_responses=True,
        )
        await self._redis.ping()
        logger.info("cache_connected")

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._redis:
            await self._redis.close()

    def _make_key(self, key: str, prefix: str | None = None) -> str:
        """Create prefixed cache key."""
        if prefix:
            return f"bookstream:{prefix}:{key}"
        return f"bookstream:{key}"

    async def get(self, key: str, prefix: str | None = None) -> Any | None:
        """Get value from cache."""
        if not self._redis:
            return None

        full_key = self._make_key(key, prefix)
        data = await self._redis.get(full_key)
        if data:
            return json.loads(data)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        prefix: str | None = None,
        ttl: int | None = None,
    ) -> None:
        """Set value in cache."""
        if not self._redis:
            return

        full_key = self._make_key(key, prefix)
        serialized = json.dumps(value, default=str)
        await self._redis.setex(
            full_key,
            ttl or self.default_ttl,
            serialized,
        )

    async def delete(self, key: str, prefix: str | None = None) -> None:
        """Delete value from cache."""
        if not self._redis:
            return

        full_key = self._make_key(key, prefix)
        await self._redis.delete(full_key)

    async def delete_pattern(self, pattern: str) -> None:
        """Delete keys matching pattern."""
        if not self._redis:
            return

        keys = await self._redis.keys(f"bookstream:{pattern}")
        if keys:
            await self._redis.delete(*keys)

    async def get_or_set(
        self,
        key: str,
        getter: callable,
        prefix: str | None = None,
        ttl: int | None = None,
    ) -> Any:
        """Get from cache or compute and store."""
        cached = await self.get(key, prefix)
        if cached is not None:
            return cached

        value = await getter()
        if value is not None:
            await self.set(key, value, prefix, ttl)
        return value

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter."""
        if not self._redis:
            return 0

        full_key = self._make_key(key)
        return await self._redis.incrby(full_key, amount)

    async def expire(self, key: str, ttl: int) -> None:
        """Set expiration on a key."""
        if not self._redis:
            return

        full_key = self._make_key(key)
        await self._redis.expire(full_key, ttl)


# Singleton
cache_service = CacheService()
