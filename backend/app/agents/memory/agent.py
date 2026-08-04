"""MemoryAgent managing session, research, and long-term workspace memory."""

from typing import Any

from app.agents.base import AgentContext, BaseAgent
from app.application.memory.memory_service import MemoryService


class MemoryAgent(BaseAgent):
    """Agent updating and retrieving long-term workspace and run memory."""

    def __init__(self, memory_service: MemoryService | None = None) -> None:
        super().__init__()
        self._memory = memory_service or MemoryService()

    @property
    def agent_name(self) -> str:
        return "memory_agent"

    async def execute(self, state: dict[str, Any], context: AgentContext) -> dict[str, Any]:
        """Update memory with latest research state."""

        run_id = context.run_id
        await self._memory.save_run_memory(
            run_id=run_id,
            memory_data={
                "objective": state.get("objective"),
                "stage": "memory_updated",
                "knowledge_count": len(state.get("knowledge_objects", [])),
            },
        )
        return {"stage": "memory"}


__all__ = ["MemoryAgent"]
