"""Telemetry and execution metrics helpers."""

import time
from typing import Any


class TelemetryService:
    """Helper service recording execution metrics, latency, and resource costs."""

    def __init__(self) -> None:
        self._metrics: list[dict[str, Any]] = []

    def record_execution(
        self, capability_id: str, duration_seconds: float, status: str = "success"
    ) -> None:
        """Record execution metric sample."""

        self._metrics.append(
            {
                "capability": capability_id,
                "duration": duration_seconds,
                "status": status,
                "timestamp": time.time(),
            }
        )


__all__ = ["TelemetryService"]
