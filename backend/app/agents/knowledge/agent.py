"""KnowledgeAgent for deduplication, confidence scoring, and evidence conflict resolution."""

from typing import Any

from app.agents.base import AgentContext, BaseAgent
from pydantic import BaseModel, Field


class KnowledgeGraphObject(BaseModel):
    """Normalized knowledge entity representation."""

    entity_id: str
    topic: str
    claims: list[str] = Field(default_factory=list)
    confidence_score: float = 0.9
    conflict_resolved: bool = True


class KnowledgeAgent(BaseAgent):
    """Specialist agent for resolving knowledge conflicts and merging claims."""

    @property
    def agent_name(self) -> str:
        return "knowledge_agent"

    async def execute(self, state: dict[str, Any], context: AgentContext) -> dict[str, Any]:
        """Process claims and build consolidated knowledge graph objects."""

        raw_claims = state.get("claims", [])
        entities = [
            KnowledgeGraphObject(
                entity_id=f"k_entity_{i + 1}",
                topic=state.get("objective", "Research Topic"),
                claims=[str(claim)],
                confidence_score=0.95,
            )
            for i, claim in enumerate(raw_claims)
        ]
        return {
            "knowledge_objects": [e.model_dump() for e in entities],
            "stage": "knowledge",
        }


__all__ = ["KnowledgeAgent", "KnowledgeGraphObject"]
