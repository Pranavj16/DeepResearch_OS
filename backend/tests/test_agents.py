"""Unit tests for Agent orchestrations."""

import pytest
from app.agents.critic.agent import CriticAgent
from app.agents.planner.agent import PlannerAgent
from app.agents.search.agent import SearchAgent
from app.agents.writer.agent import WriterAgent
from app.llm.router import LLMRouter
from app.schemas.planner import PlannerRequest
from app.tools.serper import SerperSearchClient
from pydantic import SecretStr


@pytest.mark.asyncio
async def test_planner_agent() -> None:
    router = LLMRouter()
    agent = PlannerAgent(router)
    res = await agent.plan(PlannerRequest(research_question="Deep Research Systems"))

    assert res.objective is not None
    assert len(res.steps) >= 1


@pytest.mark.asyncio
async def test_search_agent() -> None:
    agent = SearchAgent()
    results = await agent.search("AI platform")
    assert len(results) >= 1
    assert "https://" in str(results[0].url)


@pytest.mark.asyncio
async def test_serper_search_client() -> None:
    client = SerperSearchClient(api_key=SecretStr(""))
    results = await client.search("AI platform")
    assert results == []



@pytest.mark.asyncio
async def test_writer_and_critic_agents() -> None:
    router = LLMRouter()
    writer = WriterAgent(router)
    critic = CriticAgent(router)

    draft = await writer.write_report(
        objective="AI Architecture",
        evidence_claims=["Claim 1: Clean Architecture enforces isolation."],
    )
    assert draft.title is not None

    critique = await critic.review_report(
        objective="AI Architecture",
        report_text=draft.executive_summary,
    )
    assert 0.0 <= critique.quality_score <= 1.0
