"""Typed research state definition for LangGraph workflow execution."""

from typing import Annotated, Any, TypedDict
from uuid import UUID


def merge_list(left: list[Any], right: list[Any]) -> list[Any]:
    """Append list elements without duplicates."""

    res = list(left)
    for item in right:
        if item not in res:
            res.append(item)
    return res


class ResearchGraphState(TypedDict, total=False):
    """Bounded, serializable state passed between graph workflow nodes."""

    research_run_id: UUID
    execution_envelope_id: UUID
    workspace_id: UUID
    objective: str
    stage: str
    plan_steps: Annotated[list[str], merge_list]
    sources: Annotated[list[dict[str, Any]], merge_list]
    claims: Annotated[list[str], merge_list]
    draft_report: str
    critique_score: float
    critique_passed: bool
    review_required: bool
    human_approved: bool
    error_message: str | None


__all__ = ["ResearchGraphState"]
