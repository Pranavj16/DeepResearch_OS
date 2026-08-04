"""Critic Agent evaluating factual coverage, citation validity, and quality score."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.llm.models import LLMProvider
from app.llm.router import LLMRouter


class CritiqueResult(BaseModel):
    """Evaluation result emitted by the Critic Agent."""

    quality_score: float = Field(ge=0.0, le=1.0)
    passed: bool = Field(...)
    feedback: str = Field(min_length=1)
    missing_evidence: list[str] = Field(default_factory=list)


class CriticAgent:
    """Agent evaluating report factual accuracy and citation coverage."""

    def __init__(self, llm_router: LLMRouter) -> None:
        self._llm_router = llm_router

    async def review_report(
        self,
        objective: str,
        report_text: str,
        provider: LLMProvider | None = None,
        model: str | None = None,
    ) -> CritiqueResult:
        """Critique report draft for factual precision and citation coverage."""

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
            "You are a Senior Review Critic AI. Evaluate the report draft for factual depth, "
            "clarity, and citation coverage. Assign a quality score between 0.0 and 1.0."
        )
        user_prompt = f"Objective: {objective}\nReport Content:\n{report_text}"

        return await self._llm_router.generate_structured(
            provider=provider or LLMProvider.GEMINI,
            model=model or "gemini-2.5-flash",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=CritiqueResult,
        )


__all__ = ["CriticAgent", "CritiqueResult"]
