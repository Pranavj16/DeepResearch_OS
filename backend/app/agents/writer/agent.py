"""Writer Agent synthesizing evidence into formal research reports."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.llm.models import LLMProvider
from app.llm.router import LLMRouter


class ReportDraft(BaseModel):
    """Structured report draft synthesized from evidence."""

    title: str = Field(min_length=1)
    executive_summary: str = Field(min_length=1)
    key_findings: list[str] = Field(min_length=1)
    detailed_analysis: str = Field(min_length=1)
    citations: list[str] = Field(default_factory=list)


class WriterAgent:
    """Agent synthesizing verified evidence into structured report drafts."""

    def __init__(self, llm_router: LLMRouter) -> None:
        self._llm_router = llm_router

    async def write_report(
        self,
        objective: str,
        evidence_claims: list[str],
        provider: LLMProvider | None = None,
        model: str | None = None,
    ) -> ReportDraft:
        """Synthesize verified claims into a final report structure."""

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
            "You are a Senior Technical Writer AI. Synthesize the provided claims and evidence "
            "into a comprehensive, formal research report with inline citations."
        )
        claims_str = "\n".join(f"- {c}" for c in evidence_claims)
        user_prompt = f"Objective: {objective}\nVerified Evidence:\n{claims_str}"

        return await self._llm_router.generate_structured(
            provider=provider or LLMProvider.GEMINI,
            model=model or "gemini-2.5-flash",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=ReportDraft,
        )


__all__ = ["WriterAgent", "ReportDraft"]
