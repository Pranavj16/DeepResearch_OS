"""Memory subsystem service for short-lived run working memory and consent management."""

from typing import Any
from uuid import UUID

from app.db.redis import RedisAdapter


class MemoryService:
    """Service managing scoped run memory and ephemeral cache storage."""

    def __init__(self, redis_adapter: RedisAdapter | None = None) -> None:
        self._redis = redis_adapter or RedisAdapter()

    async def save_run_memory(
        self, run_id: UUID, memory_data: dict[str, Any], ttl_seconds: int = 86400
    ) -> None:
        """Persist short-lived working memory for an active research run."""

        await self._redis.cache_set(f"run_memory:{run_id}", memory_data, ttl_seconds=ttl_seconds)

    async def get_run_memory(self, run_id: UUID) -> dict[str, Any] | None:
        """Retrieve working memory for an active research run."""

        return await self._redis.cache_get(f"run_memory:{run_id}")


__all__ = ["MemoryService"]
