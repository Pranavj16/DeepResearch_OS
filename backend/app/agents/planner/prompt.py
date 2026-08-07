"""Planner Agent System Prompt definition."""

from app.agents.shared.pipeline_context import build_pipeline_system_prompt

PLANNER_SYSTEM_PROMPT = build_pipeline_system_prompt(
    agent_key="plan",
    custom_instructions="Break down the research question into logical, actionable steps with clear rationales."
)

__all__ = ["PLANNER_SYSTEM_PROMPT"]
