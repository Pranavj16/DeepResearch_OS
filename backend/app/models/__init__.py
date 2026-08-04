"""Validated platform domain contracts."""

from app.models.platform import (
    ArtifactReference,
    CapabilityDescriptor,
    EventMetadata,
    ExecutionEnvelope,
    PolicySnapshot,
)

__all__ = [
    "ArtifactReference",
    "CapabilityDescriptor",
    "EventMetadata",
    "ExecutionEnvelope",
    "PolicySnapshot",
]
