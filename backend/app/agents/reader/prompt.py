"""Reader / Extractor Agent System Prompt definition."""

from app.agents.shared.pipeline_context import build_pipeline_system_prompt

READER_SYSTEM_PROMPT = build_pipeline_system_prompt(
    agent_key="extract",
    custom_instructions="Analyze the crawled web/paper sources in the database. Extract 3-5 distinct, verified factual claims, metrics, and evidence statements with source attributions."
)

__all__ = ["READER_SYSTEM_PROMPT"]
