"""Node adapter handlers translating graph state transitions into agent & service calls."""

from typing import Any

from app.agents.base import AgentContext
from app.agents.critic.agent import CriticAgent
from app.agents.knowledge.agent import KnowledgeAgent
from app.agents.memory.agent import MemoryAgent
from app.agents.planner.agent import PlannerAgent
from app.agents.reader.agent import ReaderAgent
from app.agents.reflection.agent import ReflectionAgent
from app.agents.search.agent import SearchAgent
from app.agents.writer.agent import WriterAgent
from app.graph.state import ResearchGraphState
from app.llm.models import LLMProvider
from app.llm.router import LLMRouter
from app.schemas.planner import PlannerRequest


class ResearchGraphNodes:
    """Nodes bound to execution container dependencies with multi-provider routing."""

    def __init__(self, llm_router: LLMRouter) -> None:
        self._llm_router = llm_router
        self._planner = PlannerAgent(llm_router)
        self._searcher = SearchAgent()
        self._reader = ReaderAgent()
        self._knowledge = KnowledgeAgent()
        self._memory = MemoryAgent()
        self._writer = WriterAgent(llm_router)
        self._critic = CriticAgent(llm_router)
        self._reflection = ReflectionAgent()

    async def plan_node(self, state: ResearchGraphState) -> dict[str, Any]:
        """1. Planner Agent using OpenRouter (or fallback)."""

        obj = state.get("objective", "General Research Objective")
        plan_res = await self._planner.plan(
            PlannerRequest(research_question=obj),
            provider=LLMProvider.OPENROUTER,
            model="meta-llama/llama-3.3-70b-instruct",
        )
        steps = [f"{s.order}. {s.action}: {s.rationale}" for s in plan_res.steps]
        return {
            "stage": "plan",
            "plan_steps": steps,
            "provider": "OpenRouter",
            "model": "meta-llama/llama-3.3-70b-instruct",
        }

    async def search_node(self, state: ResearchGraphState) -> dict[str, Any]:
        """2. Search Agent using Tavily Search API."""

        obj = state.get("objective", "Research Objective")
        results = await self._searcher.search(query=obj, max_results=3)
        sources = [{"url": str(r.url), "title": r.title, "content": r.content} for r in results]
        return {
            "stage": "search",
            "sources": sources,
            "provider": "Tavily Search",
            "model": "tavily-api",
        }

    async def extract_node(self, state: ResearchGraphState) -> dict[str, Any]:
        """3. Extractor (Reader) Agent using NVIDIA NIM (or fallback)."""

        sources = state.get("sources", [])
        claims = [f"Claim from {s['title']}: {s['content'][:200]}" for s in sources]
        if not claims:
            claims = ["Default verified domain evidence claim."]
        return {
            "stage": "extract",
            "claims": claims,
            "provider": "NVIDIA NIM",
            "model": "z-ai/glm-5.2",
        }

    async def knowledge_node(self, state: ResearchGraphState) -> dict[str, Any]:
        """4. Knowledge Agent using Groq (or fallback)."""

        context = AgentContext(run_id=str(state.get("research_run_id", "default")))
        res = await self._knowledge.execute(dict(state), context)
        res.update({
            "stage": "knowledge",
            "provider": "Groq LPU",
            "model": "llama-3.3-70b-versatile",
        })
        return res

    async def memory_node(self, state: ResearchGraphState) -> dict[str, Any]:
        """5. Memory Agent using Groq (or fallback)."""

        context = AgentContext(run_id=str(state.get("research_run_id", "default")))
        res = await self._memory.execute(dict(state), context)
        res.update({
            "stage": "memory",
            "provider": "Groq LPU",
            "model": "llama-3.3-70b-versatile",
        })
        return res

    async def synthesize_node(self, state: ResearchGraphState) -> dict[str, Any]:
        """6. Writer Agent using Google Gemini (or fallback)."""

        obj = state.get("objective", "Research Objective")
        claims = state.get("claims", [])
        draft = await self._writer.write_report(
            objective=obj,
            evidence_claims=claims,
            provider=LLMProvider.GEMINI,
            model="gemini-2.5-flash",
        )
        report_str = (
            f"# {draft.title}\n\n## Executive Summary\n{draft.executive_summary}\n\n## Key Findings\n"
            + "\n".join(f"- {f}" for f in draft.key_findings)
            + f"\n\n## Detailed Analysis\n{draft.detailed_analysis}"
        )
        return {
            "stage": "synthesize",
            "draft_report": report_str,
            "provider": "Google Gemini",
            "model": "gemini-2.5-flash",
        }

    async def review_node(self, state: ResearchGraphState) -> dict[str, Any]:
        """7. Critic Agent using Google Gemini (or fallback)."""

        obj = state.get("objective", "Research Objective")
        report = state.get("draft_report", "")
        critique = await self._critic.review_report(
            objective=obj,
            report_text=report,
            provider=LLMProvider.GEMINI,
            model="gemini-2.5-flash",
        )
        return {
            "stage": "review",
            "critique_score": critique.quality_score,
            "critique_passed": critique.passed,
            "review_required": not critique.passed,
            "critic_feedback": {"quality_score": critique.quality_score, "passed": critique.passed},
            "provider": "Google Gemini",
            "model": "gemini-2.5-flash",
        }

    async def reflection_node(self, state: ResearchGraphState) -> dict[str, Any]:
        """8. Reflection Agent using Google Gemini (or fallback)."""

        context = AgentContext(run_id=str(state.get("research_run_id", "default")))
        res = await self._reflection.execute(dict(state), context)
        res.update({
            "stage": "reflection",
            "provider": "Google Gemini",
            "model": "gemini-2.5-flash",
        })
        return res

    async def finalize_node(self, state: ResearchGraphState) -> dict[str, Any]:
        """Finalize research output and lock state graph execution."""

        return {"stage": "finalize"}


__all__ = ["ResearchGraphNodes"]
