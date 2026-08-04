"""Generic Tool Interface, Registry, Loader, and Policy Manager."""

from collections.abc import Callable, Coroutine
from typing import Any

from pydantic import BaseModel

from app.exceptions.base import ValidationError
from app.models.platform import CapabilityDescriptor


class BaseTool(BaseModel):
    """Abstract tool model descriptor."""

    descriptor: CapabilityDescriptor
    handler: Callable[..., Coroutine[Any, Any, Any]]


class ToolRegistry:
    """Central registry storing tools and capabilities."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool with its capability descriptor."""

        self._tools[tool.descriptor.capability_id] = tool

    def get_tool(self, capability_id: str) -> BaseTool:
        """Fetch registered tool."""

        t = self._tools.get(capability_id)
        if not t:
            raise ValidationError(f"Tool with capability '{capability_id}' is not registered.")
        return t

    def list_tools(self) -> list[CapabilityDescriptor]:
        """List descriptors of all registered tools."""

        return [t.descriptor for t in self._tools.values()]


__all__ = ["BaseTool", "ToolRegistry"]
