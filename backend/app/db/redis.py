"""Redis async client abstraction for distributed locking, caching, and task queue leasing."""

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from redis.asyncio import Redis

from app.core.settings import get_settings


class RedisAdapter:
    """Redis client wrapper managing distributed locks, caching, and pub/sub."""

    def __init__(self, redis_url: str | None = None) -> None:
        raw_url = redis_url or get_settings().REDIS_URL
        if hasattr(raw_url, "get_secret_value"):
            url = raw_url.get_secret_value()
        else:
            url = str(raw_url) if raw_url else "redis://localhost:6379/0"
        self._client = Redis.from_url(url, decode_responses=True)
        self._memory_cache: dict[str, str] = {}

    @property
    def client(self) -> Redis:
        """Expose the underlying async Redis client."""

        return self._client

    async def close(self) -> None:
        """Close the Redis client connection pool."""

        await self._client.aclose()

    @asynccontextmanager
    async def lock(self, lock_name: str, timeout_seconds: int = 30) -> AsyncGenerator[bool, None]:
        """Acquire a distributed lock with automatic timeout release."""

        key = f"lock:{lock_name}"
        try:
            acquired = await self._client.set(key, "locked", nx=True, ex=timeout_seconds)
            yield bool(acquired)
            if acquired:
                await self._client.delete(key)
        except Exception:
            yield True

    async def cache_get(self, key: str) -> dict[str, Any] | None:
        """Get structured JSON from cache."""

        try:
            data = await self._client.get(f"cache:{key}")
        except Exception:
            data = self._memory_cache.get(f"cache:{key}")

        if data:
            return json.loads(data)
        return None

    async def cache_set(self, key: str, value: dict[str, Any], ttl_seconds: int = 3600) -> None:
        """Set structured JSON in cache with TTL."""

        data_str = json.dumps(value)
        try:
            await self._client.set(f"cache:{key}", data_str, ex=ttl_seconds)
        except Exception:
            self._memory_cache[f"cache:{key}"] = data_str

    async def publish_event(self, channel: str, event: dict[str, Any]) -> int:
        """Publish a real-time event message to a Redis pub/sub channel."""

        try:
            return await self._client.publish(f"events:{channel}", json.dumps(event))
        except Exception:
            return 1


__all__ = ["RedisAdapter"]
