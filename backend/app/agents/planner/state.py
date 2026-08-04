"""Planner Agent state aliases.

The planner is stateless; this module offers an explicit domain name for callers
that store a successfully generated planning result.
"""

from app.schemas.planner import PlannerResponse

PlannerState = PlannerResponse
