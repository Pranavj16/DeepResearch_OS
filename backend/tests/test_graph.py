"""Integration tests for LangGraph research workflow execution."""

from uuid import uuid4

import pytest
from app.graph.workflow import build_research_graph
from app.llm.router import LLMRouter


@pytest.mark.asyncio
async def test_research_graph_end_to_end_execution() -> None:
    router = LLMRouter()
    graph = build_research_graph(router)

    run_id = uuid4()
    initial_state = {
        "research_run_id": run_id,
        "objective": "Autonomous Multi-Agent Architecture",
        "stage": "intake",
    }

    final_state = await graph.ainvoke(
        initial_state,
        config={"configurable": {"thread_id": str(run_id)}},
    )

    assert final_state["stage"] == "finalize"
    assert "draft_report" in final_state
    assert len(final_state["sources"]) >= 1
