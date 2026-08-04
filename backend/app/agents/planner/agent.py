"""Planner Agent orchestration creating structured research plans."""

from __future__ import annotations

from app.llm.models import LLMProvider
from app.llm.router import LLMRouter
from app.schemas.planner import PlannerRequest, PlannerResponse


class PlannerAgent:
    """Agent creating structured research plans through the LLM Router."""

    def __init__(self, llm_router: LLMRouter) -> None:
        self._llm_router = llm_router

    async def plan(
        self,
        request: PlannerRequest,
        provider: LLMProvider | None = None,
        model: str | None = None,
    ) -> PlannerResponse:
        """Generate a structured research plan for a research question."""

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
            "You are an expert Research Planner AI. Break down the research question "
            "into logical, actionable steps with clear rationales."
        )
        user_prompt = (
            f"Research Question: {request.research_question}\nConstraints: {request.constraints}"
        )

        return await self._llm_router.generate_structured(
            provider=provider or LLMProvider.GEMINI,
            model=model or "gemini-2.5-flash",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=PlannerResponse,
        )


__all__ = ["PlannerAgent"]
