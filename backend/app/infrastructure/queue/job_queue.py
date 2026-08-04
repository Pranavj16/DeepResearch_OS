"""Job queue abstraction for future background worker scheduling."""

from typing import Any
from uuid import UUID

from app.db.redis import RedisAdapter
from app.infrastructure.persistence.postgres.repositories import JobRepository


class JobQueue:
    """Queue abstraction for scheduling and executing asynchronous platform jobs."""

    def __init__(
        self, job_repository: JobRepository, redis_adapter: RedisAdapter | None = None
    ) -> None:
        self._repo = job_repository
        self._redis = redis_adapter or RedisAdapter()

    async def enqueue_job(self, workspace_id: UUID, job_type: str, payload: dict[str, Any]) -> UUID:
        """Enqueue job in database and publish message to Redis work queue."""

        job = await self._repo.enqueue(
            workspace_id=workspace_id, job_type=job_type, payload=payload
        )
        await self._redis.publish_event("job_queue", {"job_id": str(job.id), "job_type": job_type})
        return job.id


__all__ = ["JobQueue"]
