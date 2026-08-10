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

        from app.agents.shared.pipeline_context import build_pipeline_system_prompt
        system_prompt = build_pipeline_system_prompt(
            agent_key="synthesize",
            custom_instructions=(
                "Synthesize all database assets from steps 1-5 (plan, sources, claims, knowledge objects, memory context) into an authoritative, multi-section formal research report.\n"
                "CRITICAL QUALITY INSTRUCTIONS:\n"
                "1. DO NOT use generic boilerplate phrases (like 'This formal research report provides...').\n"
                "2. Write rich, engaging, highly informative, domain-specific paragraphs with concrete insights, real-world examples, and market trends.\n"
                "3. Detailed analysis MUST include multiple structured subsections.\n"
                "4. Strategic recommendations MUST be actionable, enterprise-ready advice."
            )
        )
        steps_str = "\n".join(f"- {s}" for s in (plan_steps or []))
        claims_str = "\n".join(f"- {c}" for c in evidence_claims)
        sources_str = "\n".join(f"- {s.get('title', 'Source')}: {s.get('url', '')}" for s in (sources or []))
        know_str = "\n".join(f"- Topic: {k.get('topic')}, Claims: {k.get('claims')}" for k in (knowledge_objects or []))

        user_prompt = (
            f"RESEARCH TOPIC / OBJECTIVE: {objective}\n\n"
            f"Please write an extensive, professional deep-research report covering:\n"
            f"- Executive Summary: Strategic overview and key implications.\n"
            f"- Background & Domain Context: Historical evolution, industry drivers, and current market state.\n"
            f"- Key Research Findings: 5 to 7 detailed, high-impact research findings with domain specifics.\n"
            f"- Detailed Technical Analysis: In-depth technical breakdown with markdown headers and sub-sections.\n"
            f"- Strategic Recommendations: 4 actionable, enterprise-grade recommendations.\n"
            f"- Citations: Exact web source references.\n\n"
            f"PRIMARY INPUT EVIDENCE & SOURCES:\n"
            f"1. Research Plan Steps:\n{steps_str or 'N/A'}\n\n"
            f"2. Crawled Web Sources:\n{sources_str or 'N/A'}\n\n"
            f"3. Verified Evidence Claims:\n{claims_str or 'N/A'}\n\n"
            f"4. Knowledge Graph Context:\n{know_str or 'N/A'}\n\n"
            f"5. Memory Context:\n{memory_context or 'N/A'}"
        )

        return await self._llm_router.generate_structured(
            provider=provider or LLMProvider.GEMINI,
            model=model or "gemini-2.5-flash",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=ReportDraft,
        )


__all__ = ["WriterAgent", "ReportDraft"]
