"""Automated test suite for Specialist Agents and LangGraph Research Engine."""

from uuid import uuid4

import pytest
from app.agents.base import AgentContext
from app.agents.knowledge.agent import KnowledgeAgent
from app.agents.memory.agent import MemoryAgent
from app.agents.reflection.agent import ReflectionAgent
from app.graph.workflow import build_research_graph
from app.llm.router import LLMRouter


@pytest.mark.asyncio
async def test_specialist_agents_execution() -> None:
    context = AgentContext(run_id=str(uuid4()))

    k_agent = KnowledgeAgent()
    k_res = await k_agent.execute({"claims": ["Evidence Claim 1", "Evidence Claim 2"]}, context)
    assert len(k_res["knowledge_objects"]) == 2

    m_agent = MemoryAgent()
    m_res = await m_agent.execute({"objective": "Test Memory"}, context)
    assert m_res["stage"] == "memory"

    r_agent = ReflectionAgent()
    r_res = await r_agent.execute(
        {"critic_feedback": {"quality_score": 0.95, "passed": True}}, context
    )
    assert r_res["reflection_decision"]["requires_revision"] is False


@pytest.mark.asyncio
async def test_langgraph_full_pipeline_execution() -> None:
    router = LLMRouter()
    graph = build_research_graph(router)

    run_id = uuid4()
    initial_state = {
        "research_run_id": run_id,
        "objective": "Autonomous AI Research Engine Architecture",
        "stage": "intake",
    }

    final_state = await graph.ainvoke(
        initial_state,
        config={"configurable": {"thread_id": str(run_id)}},
    )

    assert final_state["stage"] == "finalize"
    assert "draft_report" in final_state
