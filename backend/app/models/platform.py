"""Core platform contracts shared by execution, capability, and knowledge layers."""

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

TrustLevel = Literal["trusted", "verified", "untrusted"]
SideEffect = Literal["none", "network", "external_write", "code_execution"]
Sensitivity = Literal["public", "internal", "confidential", "restricted"]
RetentionClass = Literal["ephemeral", "standard", "long_term", "legal_hold"]


class PlatformContract(BaseModel):
    """Immutable validated contract base for platform boundary objects."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class PolicySnapshot(PlatformContract):
    """Policy version captured when an execution is authorized."""

    policy_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    digest: str = Field(min_length=1)


class CapabilityDescriptor(PlatformContract):
    """Published capability metadata used for discovery and authorization."""

    capability_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    input_schema: str = Field(min_length=1)
    output_schema: str = Field(min_length=1)
    trust_level: TrustLevel
    side_effects: frozenset[SideEffect] = frozenset({"none"})
    modalities: frozenset[str] = frozenset({"text"})
    required_permissions: frozenset[str] = frozenset()
    limits: dict[str, int] = Field(default_factory=dict)

    @field_validator("limits")
    @classmethod
    def validate_limits(cls, limits: dict[str, int]) -> dict[str, int]:
        """Reject negative capability resource limits."""

        if any(value < 0 for value in limits.values()):
            raise ValueError("Capability limits cannot be negative.")
        return limits


class ArtifactReference(PlatformContract):
    """Immutable reference to content stored outside the transactional record."""

    artifact_id: UUID = Field(default_factory=uuid4)
    uri: str = Field(min_length=1)
    content_hash: str = Field(min_length=1)
    media_type: str = Field(min_length=1)
    sensitivity: Sensitivity = "internal"
    retention: RetentionClass = "standard"
    lineage: tuple[UUID, ...] = ()


class ExecutionEnvelope(PlatformContract):
    """Authorization, budget, trace, and tenancy context for one execution."""

    execution_id: UUID = Field(default_factory=uuid4)
    principal_id: UUID
    organization_id: UUID
    project_id: UUID
    workspace_id: UUID
    environment_id: UUID
    policy: PolicySnapshot
    parent_execution_id: UUID | None = None
    idempotency_key: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    deadline: datetime
    budget: dict[str, int] = Field(default_factory=dict)
    cancellation_requested: bool = False
    artifact_references: tuple[ArtifactReference, ...] = ()

    @field_validator("deadline")
    @classmethod
    def require_timezone(cls, deadline: datetime) -> datetime:
        """Require an unambiguous UTC-aware execution deadline."""

        if deadline.tzinfo is None or deadline.utcoffset() is None:
            raise ValueError("Execution deadline must include timezone information.")
        return deadline.astimezone(UTC)

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, budget: dict[str, int]) -> dict[str, int]:
        """Reject negative execution budgets."""

        if any(value < 0 for value in budget.values()):
            raise ValueError("Execution budgets cannot be negative.")
        return budget


class EventMetadata(PlatformContract):
    """Causation and ordering metadata for durable platform events."""

    event_id: UUID = Field(default_factory=uuid4)
    event_type: str = Field(min_length=1)
    schema_version: int = Field(default=1, ge=1)
    aggregate_id: UUID
    ordering_key: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    causation_id: UUID | None = None
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    producer: str = Field(min_length=1)
    retention: RetentionClass = "standard"


__all__ = [
    "ArtifactReference",
    "CapabilityDescriptor",
    "EventMetadata",
    "ExecutionEnvelope",
    "PolicySnapshot",
    "PlatformContract",
]
