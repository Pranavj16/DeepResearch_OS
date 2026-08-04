"""Platform domain contract tests."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from app.models import ArtifactReference, CapabilityDescriptor, ExecutionEnvelope, PolicySnapshot
from pydantic import ValidationError


def _envelope() -> ExecutionEnvelope:
    """Build a valid execution envelope for contract tests."""

    return ExecutionEnvelope(
        principal_id=uuid4(),
        organization_id=uuid4(),
        project_id=uuid4(),
        workspace_id=uuid4(),
        environment_id=uuid4(),
        policy=PolicySnapshot(policy_id="policy", version="1", digest="sha256:digest"),
        idempotency_key="request-1",
        correlation_id="correlation-1",
        deadline=datetime.now(UTC) + timedelta(minutes=5),
    )


def test_execution_envelope_normalizes_deadline_to_utc() -> None:
    """Execution context must preserve unambiguous timezone-aware deadlines."""

    envelope = _envelope()

    assert envelope.deadline.tzinfo is not None
    assert envelope.deadline.utcoffset() == timedelta(0)


def test_capability_and_artifact_contracts_are_immutable() -> None:
    """Published capability and artifact metadata must not mutate in place."""

    capability = CapabilityDescriptor(
        capability_id="reader",
        version="1.0.0",
        display_name="Reader",
        input_schema="reader.request.v1",
        output_schema="reader.result.v1",
        trust_level="verified",
    )
    artifact = ArtifactReference(
        uri="s3://bucket/artifact",
        content_hash="sha256:artifact",
        media_type="text/plain",
    )

    with pytest.raises(ValidationError):
        capability.display_name = "Changed"  # type: ignore[misc]
    assert artifact.retention == "standard"


def test_platform_contracts_reject_unsafe_budget_and_deadline() -> None:
    """Negative budgets and naive deadlines must fail validation."""

    with pytest.raises(ValidationError):
        ExecutionEnvelope.model_validate({**_envelope().model_dump(), "budget": {"tokens": -1}})

    with pytest.raises(ValidationError):
        ExecutionEnvelope(
            principal_id=uuid4(),
            organization_id=uuid4(),
            project_id=uuid4(),
            workspace_id=uuid4(),
            environment_id=uuid4(),
            policy=PolicySnapshot(policy_id="policy", version="1", digest="digest"),
            idempotency_key="request-1",
            correlation_id="correlation-1",
            deadline=datetime.now(),
        )
