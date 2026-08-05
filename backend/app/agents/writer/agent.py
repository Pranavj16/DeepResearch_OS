"""Writer Agent synthesizing evidence into formal research reports."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from app.llm.models import LLMProvider
from app.llm.router import LLMRouter


class ReportDraft(BaseModel):
    """Structured report draft synthesized from evidence."""

    title: str = Field(min_length=1)
    executive_summary: str = Field(min_length=1)
    background_context: str = Field(default="Foundational context and domain background.")
    key_findings: list[str] = Field(min_length=1)
    detailed_analysis: str = Field(min_length=1)
    strategic_recommendations: list[str] = Field(default_factory=lambda: ["Continue domain monitoring and evidence verification."])
    citations: list[str] = Field(default_factory=list)


class WriterAgent:
    """Agent synthesizing verified evidence into structured report drafts."""

    def __init__(self, llm_router: LLMRouter) -> None:
        self._llm_router = llm_router

    async def write_report(
        self,
        objective: str,
        evidence_claims: list[str],
        plan_steps: list[str] | None = None,
        sources: list[dict[str, Any]] | None = None,
        knowledge_objects: list[dict[str, Any]] | None = None,
        memory_context: str | None = None,
        provider: LLMProvider | None = None,
        model: str | None = None,
    ) -> ReportDraft:
        """Synthesize verified claims, plan steps, and source citations into a final report structure."""

        available = self._llm_router.available_providers()
        if not provider or provider not in available:
            if LLMProvider.GEMINI in available:
                provider = LLMProvider.GEMINI
                model = "gemini-2.5-flash"
            elif LLMProvider.GROQ in available:
                provider = LLMProvider.GROQ
                model = "llama-3.3-70b-versatile"
            elif LLMProvider.OPENROUTER in available:
                provider = LLMProvider.OPENROUTER
                model = "meta-llama/llama-3.3-70b-instruct"
            elif LLMProvider.NVIDIA in available:
                provider = LLMProvider.NVIDIA
                model = "z-ai/glm-5.2"
            elif available:
                provider = available[0]

        system_prompt = (
            "You are a Senior Technical Writer AI. Synthesize the provided research plan, "
            "crawled source evidence, knowledge graph entities, and working memory "
            "into a comprehensive, formal, multi-section research report with inline citations."
        )
        steps_str = "\n".join(f"- {s}" for s in (plan_steps or []))
        claims_str = "\n".join(f"- {c}" for c in evidence_claims)
        sources_str = "\n".join(f"- {s.get('title', 'Source')}: {s.get('url', '')}" for s in (sources or []))
        know_str = "\n".join(f"- Topic: {k.get('topic')}, Claims: {k.get('claims')}" for k in (knowledge_objects or []))

        user_prompt = (
            f"Research Objective: {objective}\n\n"
            f"1. Research Plan Steps (Planner Agent Output):\n{steps_str or 'N/A'}\n\n"
            f"2. Crawled Web Sources (Search Agent Output):\n{sources_str or 'N/A'}\n\n"
            f"3. Verified Evidence Claims (Extractor Agent Output):\n{claims_str or 'N/A'}\n\n"
            f"4. Knowledge Graph Matrix (Knowledge Agent Output):\n{know_str or 'N/A'}\n\n"
            f"5. Agent Memory Context (Memory Agent Output):\n{memory_context or 'N/A'}"
        )

        return await self._llm_router.generate_structured(
            provider=provider or LLMProvider.GEMINI,
            model=model or "gemini-2.5-flash",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=ReportDraft,
        )


__all__ = ["WriterAgent", "ReportDraft"]
