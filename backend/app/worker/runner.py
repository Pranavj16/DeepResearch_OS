"""Background worker process entrypoint for task leasing and job execution."""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from app.core.logging import setup_logging
from app.db.models import TaskLeaseModel
from app.db.postgres import create_engine_from_url, create_session_factory
from app.graph.workflow import build_research_graph
from app.llm.router import LLMRouter


class TaskWorker:
    """Worker process claiming and processing durable research tasks."""

    def __init__(self, worker_id: str = "worker-1") -> None:
        self.worker_id = worker_id
        self.running = False
        self._engine = create_engine_from_url()
        self._session_factory = create_session_factory(self._engine)
        self._llm_router = LLMRouter()

    async def start(self) -> None:
        """Run worker task loop."""

        setup_logging()
        self.running = True

        while self.running:
            async with self._session_factory() as session:
                # Cleanup expired task leases
                now = datetime.now(UTC)
                # Task claim logic loop stub
                lease = TaskLeaseModel(
                    task_id=f"task_{now.timestamp()}",
                    worker_id=self.worker_id,
                    expires_at=now + timedelta(minutes=5),
                )
                session.add(lease)
                await session.commit()

            await asyncio.sleep(10)

    async def execute_run(self, run_id: UUID, objective: str) -> dict[str, Any]:
        """Process a single research run task."""

        graph = build_research_graph(self._llm_router)
        state = {
            "research_run_id": run_id,
            "objective": objective,
            "stage": "intake",
        }
        return await graph.ainvoke(state, config={"configurable": {"thread_id": str(run_id)}})

    def stop(self) -> None:
        """Signal worker shutdown."""

        self.running = False


__all__ = ["TaskWorker"]
