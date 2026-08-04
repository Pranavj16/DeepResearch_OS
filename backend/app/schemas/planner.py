"""Pydantic contracts owned by the Planner Agent."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PlannerRequest(BaseModel):
    """Input required to create a research plan."""

    research_question: str = Field(min_length=1, description="Question to plan research for.")
    constraints: list[str] = Field(
        default_factory=list,
        description="Optional requirements that should shape the plan.",
    )


class PlanStep(BaseModel):
    """One ordered, actionable step in a research plan."""

    order: int = Field(ge=1, description="One-based execution order.")
    action: str = Field(min_length=1, description="Action to take during this step.")
    rationale: str = Field(min_length=1, description="Why this step is needed.")


class PlannerResponse(BaseModel):
    """Structured research plan produced by the Planner Agent."""

    objective: str = Field(min_length=1, description="Restated research objective.")
    steps: list[PlanStep] = Field(min_length=1, description="Ordered plan steps.")
    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made while forming the plan.",
    )
