"""Critic Agent System Prompt definition."""

from app.agents.shared.pipeline_context import build_pipeline_system_prompt

CRITIC_SYSTEM_PROMPT = build_pipeline_system_prompt(
    agent_key="review",
    custom_instructions="Evaluate the report draft synthesized in step 6 against database evidence claims extracted in step 3. Audit citation validity and assign a quality score between 0.0 and 1.0."
)

__all__ = ["CRITIC_SYSTEM_PROMPT"]
