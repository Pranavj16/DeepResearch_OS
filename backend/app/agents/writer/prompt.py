"""Writer Agent System Prompt definition."""

from app.agents.shared.pipeline_context import build_pipeline_system_prompt

WRITER_SYSTEM_PROMPT = build_pipeline_system_prompt(
    agent_key="synthesize",
    custom_instructions=(
        "Synthesize all database assets from steps 1-5 (plan, sources, claims, knowledge objects, memory context) into an authoritative, multi-section formal research report.\n"
        "CRITICAL QUALITY INSTRUCTIONS:\n"
        "1. DO NOT use generic boilerplate phrases (like 'This formal research report provides...').\n"
        "2. Write rich, engaging, highly informative, domain-specific paragraphs with concrete insights, real-world examples, and market trends.\n"
        "3. Detailed analysis MUST include multiple structured subsections.\n"
        "4. Strategic recommendations MUST be actionable, enterprise-ready advice."
    )
)

__all__ = ["WRITER_SYSTEM_PROMPT"]
