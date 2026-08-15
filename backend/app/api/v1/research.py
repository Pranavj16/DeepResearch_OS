"""Research run command and query API resource endpoints."""

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import CreateResearchRunRequest, ResearchRunResponse
from app.application.workspace.service import WorkspaceService
from app.core.dependencies import get_llm_router
from app.db.models import ExecutionEnvelopeModel, PolicySnapshotModel, ResearchRunModel
from app.db.postgres import (
    create_engine_from_url,
    create_session_factory,
    ensure_tables_created,
)
from app.graph.workflow import build_research_graph
from app.llm.router import LLMRouter

router = APIRouter(prefix="/research", tags=["Research"])


async def get_session() -> AsyncSession:
    """FastAPI session dependency using local engine factory with automatic table assurance."""

    engine = create_engine_from_url()
    await ensure_tables_created(engine)
    session_factory = create_session_factory(engine)
    async with session_factory() as session:
        yield session


async def _execute_graph_in_background(
    run_id: UUID,
    execution_id: UUID,
    workspace_id: UUID,
    objective: str,
    llm_router: LLMRouter,
):
    """Execute LangGraph multi-agent research graph asynchronously with real-time DB stage updates."""
    engine = create_engine_from_url()
    session_factory = create_session_factory(engine)
    async with session_factory() as session:
        stmt = select(ResearchRunModel).where(ResearchRunModel.id == run_id)
        res = await session.execute(stmt)
        run = res.scalar_one_or_none()
        if not run:
            return

        try:
            graph = build_research_graph(llm_router)
            initial_state = {
                "research_run_id": run.id,
                "execution_envelope_id": execution_id,
                "workspace_id": workspace_id,
                "objective": objective,
                "stage": "intake",
            }

            final_state = dict(initial_state)

            # Stream execution node-by-node so DB updates in real time
            async for output in graph.astream(
                initial_state,
                config={"configurable": {"thread_id": str(run.id)}},
            ):
                for node_name, node_output in output.items():
                    if isinstance(node_output, dict):
                        final_state.update(node_output)
                        stage_val = node_output.get("stage", node_name)
                        run.stage = stage_val

                        # Always initialize current_details from database
                        current_details = dict(run.details or {})

                        # Preserve accumulative agent outputs in database
                        if "plan_steps" in node_output:
                            current_details["plan_steps"] = node_output["plan_steps"]
                        if "sources" in node_output:
                            current_details["sources"] = node_output["sources"]
                        if "claims" in node_output:
                            current_details["claims"] = node_output["claims"]
                        if "knowledge_objects" in node_output:
                            current_details["knowledge_objects"] = node_output["knowledge_objects"]
                        if "memory_context" in node_output:
                            current_details["memory_context"] = node_output["memory_context"]
                        if "draft_report" in node_output:
                            current_details["draft_report"] = node_output["draft_report"]
                            run.result_summary = node_output["draft_report"]
                        if "critique_score" in node_output:
                            current_details["critique_score"] = node_output["critique_score"]
                            current_details["critique_passed"] = node_output.get("critique_passed", True)

                        # Append real-time agent execution tracking log to DB
                        agent_logs = list(current_details.get("agent_logs") or [])
                        agent_name_map = {
                            "plan": "Planner Agent",
                            "search": "Searcher Agent",
                            "extract": "Extractor / Reader Agent",
                            "knowledge": "Knowledge Agent",
                            "memory": "Memory Agent",
                            "synthesize": "Writer Agent",
                            "review": "Critic Agent",
                            "reflection": "Reflection Agent",
                            "finalize": "Finalize Engine",
                        }
                        
                        summary_text = "Stage completed"
                        if "plan_steps" in node_output:
                            summary_text = f"Generated {len(node_output['plan_steps'])} research sub-goals"
                        elif "sources" in node_output:
                            summary_text = f"Crawled {len(node_output['sources'])} web/paper sources"
                        elif "claims" in node_output:
                            summary_text = f"Extracted {len(node_output['claims'])} verified factual claims"
                        elif "knowledge_objects" in node_output:
                            summary_text = f"Built {len(node_output['knowledge_objects'])} RAG graph objects"
                        elif "memory_context" in node_output:
                            summary_text = "Checkpointed working memory state"
                        elif "draft_report" in node_output:
                            summary_text = f"Synthesized research report ({len(node_output['draft_report'])} chars)"
                        elif "critique_score" in node_output:
                            summary_text = f"Audited quality score: {node_output['critique_score']}"

                        agent_logs.append({
                            "step": len(agent_logs) + 1,
                            "stage": stage_val,
                            "agent": agent_name_map.get(stage_val, f"{stage_val.capitalize()} Agent"),
                            "timestamp": datetime.now(UTC).isoformat(),
                            "status": "completed",
                            "summary": summary_text,
                        })
                        current_details["agent_logs"] = agent_logs

                        run.details = current_details
                        await session.commit()

            run.status = "completed"
            run.stage = final_state.get("stage", "finalize")
            run.result_summary = final_state.get("draft_report", "Research finished.")
            details_dict = dict(run.details or {})
            details_dict["draft_report"] = final_state.get("draft_report", "")
            run.details = details_dict
            await session.commit()
        except Exception as err:
            run.status = "failed"
            run.result_summary = str(err)
            run.details = {"error": str(err)}
            await session.commit()


@router.post("/runs", response_model=ResearchRunResponse, status_code=status.HTTP_201_CREATED)
async def create_research_run(
    payload: CreateResearchRunRequest,
    session: AsyncSession = Depends(get_session),
    llm_router: LLMRouter = Depends(get_llm_router),
) -> ResearchRunResponse:
    """Create and trigger a durable autonomous research run asynchronously."""

    ws_service = WorkspaceService(session)
    org, proj, ws, env, user = await ws_service.get_or_create_default_tenancy(payload.user_email)

    policy = PolicySnapshotModel(policy_id="default_v1", version="1.0.0", digest="sha256:v1")
    session.add(policy)
    await session.flush()

    envelope = ExecutionEnvelopeModel(
        principal_id=user.id,
        organization_id=org.id,
        project_id=proj.id,
        workspace_id=ws.id,
        environment_id=env.id,
        policy_snapshot_id=policy.id,
        idempotency_key=f"run_idemp_{uuid4().hex[:8]}",
        correlation_id=f"corr_{uuid4().hex[:8]}",
        deadline=datetime.now(UTC) + timedelta(hours=2),
        budget={"tokens": payload.budget_tokens},
    )
    session.add(envelope)
    await session.flush()

    run = ResearchRunModel(
        execution_id=envelope.id,
        workspace_id=ws.id,
        title=payload.title,
        objective=payload.objective,
        status="running",
        stage="intake",
    )
    session.add(run)
    await session.commit()

    # Trigger background execution task immediately without blocking HTTP response
    asyncio.create_task(
        _execute_graph_in_background(
            run.id, envelope.id, ws.id, payload.objective, llm_router
        )
    )

    return ResearchRunResponse(
        id=run.id,
        execution_id=run.execution_id,
        workspace_id=run.workspace_id,
        status=run.status,
        title=run.title,
        objective=run.objective,
        stage=run.stage,
        result_summary=run.result_summary,
        details=run.details or {},
        created_at=run.created_at,
    )


@router.get("/history", response_model=list[ResearchRunResponse])
@router.get("/runs", response_model=list[ResearchRunResponse])
async def list_research_runs(
    user_email: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
    limit: int = 50,
) -> list[ResearchRunResponse]:
    """List recent research runs isolated to the user's workspace."""

    stmt = select(ResearchRunModel)
    if user_email:
        ws_service = WorkspaceService(session)
        org, proj, ws, env, user = await ws_service.get_or_create_default_tenancy(user_email)
        stmt = stmt.where(ResearchRunModel.workspace_id == ws.id)

    stmt = stmt.order_by(ResearchRunModel.created_at.desc()).limit(limit)
    res = await session.execute(stmt)
    runs = res.scalars().all()

    return [
        ResearchRunResponse(
            id=run.id,
            execution_id=run.execution_id,
            workspace_id=run.workspace_id,
            status=run.status,
            title=run.title,
            objective=run.objective,
            stage=run.stage,
            result_summary=run.result_summary,
            details=run.details or {},
            created_at=run.created_at,
        )
        for run in runs
    ]


@router.get("/runs/{run_id}", response_model=ResearchRunResponse)
async def get_research_run(
    run_id: str,
    user_email: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> ResearchRunResponse:
    """Retrieve details for a research run isolated by user workspace."""

    clean_id = run_id.replace("-", "").lower()
    stmt = select(ResearchRunModel)

    if user_email:
        ws_service = WorkspaceService(session)
        org, proj, ws, env, user = await ws_service.get_or_create_default_tenancy(user_email)
        stmt = stmt.where(ResearchRunModel.workspace_id == ws.id)

    res = await session.execute(stmt)
    all_runs = res.scalars().all()
    run = None
    for r in all_runs:
        if str(r.id).replace("-", "").lower() == clean_id:
            run = r
            break

    if not run:
        raise HTTPException(status_code=404, detail=f"Research run {run_id} not found.")

    return ResearchRunResponse(
        id=run.id,
        execution_id=run.execution_id,
        workspace_id=run.workspace_id,
        status=run.status,
        title=run.title,
        objective=run.objective,
        stage=run.stage,
        result_summary=run.result_summary,
        details=run.details or {},
        created_at=run.created_at,
    )


@router.api_route("/runs/{run_id}", methods=["DELETE", "POST"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_run(
    run_id: str,
    user_email: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a research run isolated by user workspace."""

    clean_id = run_id.replace("-", "").lower()
    stmt = select(ResearchRunModel)

    if user_email:
        ws_service = WorkspaceService(session)
        org, proj, ws, env, user = await ws_service.get_or_create_default_tenancy(user_email)
        stmt = stmt.where(ResearchRunModel.workspace_id == ws.id)

    res = await session.execute(stmt)
    all_runs = res.scalars().all()
    run = None
    for r in all_runs:
        if str(r.id).replace("-", "").lower() == clean_id:
            run = r
            break

    if not run:
        raise HTTPException(status_code=404, detail=f"Research run {run_id} not found.")

    execution_id = run.execution_id
    await session.delete(run)
    await session.commit()

    if execution_id:
        try:
            env = await session.get(ExecutionEnvelopeModel, execution_id)
            if env:
                await session.delete(env)
                await session.commit()
        except Exception:
            pass
