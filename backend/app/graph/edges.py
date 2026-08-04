"""Conditional routing edges for research graph state machine."""

from typing import Literal

from app.graph.state import ResearchGraphState


def route_after_review(
    state: ResearchGraphState,
) -> Literal["finalize", "synthesize"]:
    """Route execution based on quality review score and critique pass status."""

    passed = state.get("critique_passed", True)
    if passed:
        return "finalize"
    return "synthesize"


__all__ = ["route_after_review"]
