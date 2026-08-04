"""BaseAgent framework providing lifecycle, tracing, LLM access,
and error handling for all specialist agents."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from app.core.telemetry import TelemetryService
from app.llm.router import LLMRouter


class AgentContext(BaseModel):
    """Execution context provided to agents."""

    run_id: str
    workspace_id: str = "default"
    correlation_id: str = "default-corr-id"


class BaseAgent(ABC):
    """Abstract BaseAgent class enforcing lifecycle, validation, metrics, and error boundaries."""

    def __init__(self, llm_router: LLMRouter | None = None) -> None:
        self._router = llm_router or LLMRouter()
        self._telemetry = TelemetryService()

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return unique agent identifier."""
        pass

    @abstractmethod
    async def execute(self, state: dict[str, Any], context: AgentContext) -> dict[str, Any]:
        """Execute agent business logic."""
        pass


__all__ = ["AgentContext", "BaseAgent"]
