"""API transport contracts for public endpoints."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CreateResearchRunRequest(BaseModel):
    """Payload to initiate a new research run."""

    title: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    user_email: str = Field(default="user@research.ai")
    budget_tokens: int = Field(default=100000, ge=1000)


class ResearchRunResponse(BaseModel):
    """Response representing a research run."""

    id: UUID
    execution_id: UUID
    workspace_id: UUID
    status: str
    title: str
    objective: str
    stage: str
    result_summary: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class HealthCheckResponse(BaseModel):
    """System health status payload."""

    status: str
    version: str
    database: str = "ok"
    redis: str = "ok"
    qdrant: str = "ok"


__all__ = [
    "CreateResearchRunRequest",
    "HealthCheckResponse",
    "ResearchRunResponse",
]
