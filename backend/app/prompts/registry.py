"""Centralized Prompt Management Registry, System Prompts, and Versioning."""

from typing import Any

from pydantic import BaseModel, Field

from app.exceptions.base import ValidationError


class PromptTemplate(BaseModel):
    """Structured prompt template definition."""

    name: str
    version: str = "1.0.0"
    system_prompt: str
    template: str
    variables: list[str] = Field(default_factory=list)

    def render(self, **kwargs: Any) -> tuple[str, str]:
        """Render system prompt and user prompt with variables."""

        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            raise ValidationError(f"Missing required prompt variables: {missing}")

        rendered_user = self.template.format(**kwargs)
        return self.system_prompt, rendered_user


class PromptRegistry:
    """Central registry storing and versioning system prompts."""

    def __init__(self) -> None:
        self._prompts: dict[str, PromptTemplate] = {}
        self._bootstrap_default_prompts()

    def _bootstrap_default_prompts(self) -> None:
        """Register default system prompt templates."""

        self.register(
            PromptTemplate(
                name="planner_system",
                system_prompt=(
                    "You are an expert Lead Research Planner. "
                    "Break down research goals into structured steps."
                ),
                template="Research Objective: {objective}",
                variables=["objective"],
            )
        )
        self.register(
            PromptTemplate(
                name="writer_system",
                system_prompt=(
                    "You are a Senior Technical Writer synthesizing evidence "
                    "into authoritative research reports."
                ),
                template="Objective: {objective}\nEvidence Claims:\n{evidence}",
                variables=["objective", "evidence"],
            )
        )
        self.register(
            PromptTemplate(
                name="critic_system",
                system_prompt=(
                    "You are a Factual Reflection Critic reviewing research reports "
                    "for citation coverage and accuracy."
                ),
                template="Draft Title: {title}\nContent:\n{content}",
                variables=["title", "content"],
            )
        )

    def register(self, template: PromptTemplate) -> None:
        """Register prompt template."""

        self._prompts[template.name] = template

    def get(self, name: str) -> PromptTemplate:
        """Fetch prompt template by name."""

        p = self._prompts.get(name)
        if not p:
            raise ValidationError(f"Prompt template '{name}' not found in registry.")
        return p


__all__ = ["PromptRegistry", "PromptTemplate"]
