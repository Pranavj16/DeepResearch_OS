"""Server-Sent Events (SSE) streaming router for live progress updates."""

import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import select
from starlette.responses import StreamingResponse

from app.db.models import ResearchRunModel
from app.db.postgres import Base, create_engine_from_url, create_session_factory

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/stream/{run_id}")
async def stream_run_events(run_id: str) -> StreamingResponse:
    """Stream real-time SSE progress events for a research run from database."""

    async def event_generator() -> AsyncGenerator[str, None]:
        clean_id = run_id.replace("-", "").lower()
        engine = create_engine_from_url()

        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception:
            pass

        session_factory = create_session_factory(engine)

        last_stage = None
        last_status = None
        max_checks = 600  # Max 10 minutes streaming timeout

        for _ in range(max_checks):
            run = None
            try:
                async with session_factory() as session:
                    stmt = select(ResearchRunModel)
                    res = await session.execute(stmt)
                    all_runs = res.scalars().all()
                    for r in all_runs:
                        if str(r.id).replace("-", "").lower() == clean_id:
                            run = r
                            break
            except Exception:
                run = None

                if run:
                    current_stage = run.stage or "intake"
                    current_status = run.status or "running"
                    details = run.details or {}

                    if current_stage != last_stage or current_status != last_status:
                        last_stage = current_stage
                        last_status = current_status

                        ev_payload = {
                            "event": "completed" if current_status == "completed" else "stage_changed",
                            "stage": current_stage,
                            "status": current_status,
                            "run_id": str(run.id),
                            "title": run.title,
                            "objective": run.objective,
                            "timestamp": datetime.now(UTC).isoformat(),
                            "payload": {
                                "sources": details.get("sources", []),
                                "claims": details.get("claims", []),
                                "writer_stream": details.get("draft_report") or run.result_summary or "",
                                "critique_score": details.get("critique_score"),
                            },
                        }
                        yield f"data: {json.dumps(ev_payload)}\n\n"

                        if current_status in ["completed", "failed"]:
                            break

            await asyncio.sleep(1.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


__all__ = ["router"]
