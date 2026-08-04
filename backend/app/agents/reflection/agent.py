"""ReflectionAgent evaluating Critic feedback and directing report revision loops."""

from typing import Any

from app.agents.base import AgentContext, BaseAgent
from pydantic import BaseModel


class ReflectionDecision(BaseModel):
    """Decision object governing revision loops."""

    requires_revision: bool
    quality_score: float
    directive: str


class ReflectionAgent(BaseAgent):
    """Specialist agent performing self-reflection and governing graph revision loops."""

    @property
    def agent_name(self) -> str:
        return "reflection_agent"

    async def execute(self, state: dict[str, Any], context: AgentContext) -> dict[str, Any]:
        """Evaluate critique quality and decide on revision loop."""

        critique = state.get("critic_feedback", {})
        score = critique.get("quality_score", 0.9)
        passed = critique.get("passed", True)

        requires_revision = not passed or score < 0.7
        decision = ReflectionDecision(
            requires_revision=requires_revision,
            quality_score=score,
            directive="Enhance section depth and verify inline citation spans"
            if requires_revision
            else "Report satisfies factual quality standards.",
        )

        return {
            "reflection_decision": decision.model_dump(),
            "stage": "reflection",
        }


__all__ = ["ReflectionAgent", "ReflectionDecision"]
