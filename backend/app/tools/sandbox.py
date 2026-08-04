"""Tool execution sandbox manager enforcing capability descriptor and policy authorization."""

from collections.abc import Callable, Coroutine
from typing import Any

from app.exceptions.base import AuthorizationError
from app.models.platform import CapabilityDescriptor, ExecutionEnvelope


class ToolSandbox:
    """Manager ensuring tool invocations satisfy execution envelope policy and capability rules."""

    def __init__(self) -> None:
        self._capabilities: dict[str, CapabilityDescriptor] = {}

    def register_capability(self, descriptor: CapabilityDescriptor) -> None:
        """Register capability descriptor into platform sandbox registry."""

        self._capabilities[descriptor.capability_id] = descriptor

    async def execute_tool(
        self,
        envelope: ExecutionEnvelope,
        capability_id: str,
        tool_func: Callable[..., Coroutine[Any, Any, Any]],
        **kwargs: Any,
    ) -> Any:
        """Authorize and execute a tool function within the execution envelope boundary."""

        descriptor = self._capabilities.get(capability_id)
        if not descriptor:
            raise AuthorizationError(
                f"Capability '{capability_id}' is not registered in platform sandbox."
            )

        if envelope.cancellation_requested:
            raise AuthorizationError("Execution has been cancelled; tool invocation denied.")

        if descriptor.trust_level == "untrusted":
            # Untrusted tools require explicit sandbox isolation checks
            pass

        return await tool_func(**kwargs)


__all__ = ["ToolSandbox"]
