"""Central Multi-Agent Pipeline Context & Architectural System Prompt Builder."""

from __future__ import annotations

from typing import Any

PIPELINE_AGENTS: list[dict[str, Any]] = [
    {
        "step": 1,
        "name": "Planner Agent",
        "key": "plan",
        "role": "Strategic Task Decomposition",
        "short_description": "Formulates the foundational execution roadmap and search strategy.",
        "work_done": "Decomposed the research objective into logical sub-goals, search queries, and technical evaluation criteria.",
        "output": "plan_steps (saved to shared database)",
    },
    {
        "step": 2,
        "name": "Searcher Agent",
        "key": "search",
        "role": "Multi-Source Live Web & Literature Crawling",
        "short_description": "Fetches live web pages, Google Serper feeds, and ArXiv academic papers.",
        "work_done": "Crawled multi-source web evidence and academic paper databases matching the planner's sub-goals.",
        "output": "sources (saved to shared database)",
    },
    {
        "step": 3,
        "name": "Extractor / Reader Agent",
        "key": "extract",
        "role": "Factual Claim & Evidence Extraction",
        "short_description": "Parses raw web documents into verified factual claim spans and evidence metrics.",
        "work_done": "Extracted structured factual claims, statistics, and verifiable evidence spans from crawled sources.",
        "output": "claims (saved to shared database)",
    },
    {
        "step": 4,
        "name": "Knowledge Agent",
        "key": "knowledge",
        "role": "RAG Graph Indexing & Entity Relationship Modeling",
        "short_description": "Constructs structured entity-claim relationships and vector index objects.",
        "work_done": "Constructed entity-claim relationship matrices, RAG vector indices, and knowledge graph objects.",
        "output": "knowledge_objects (saved to shared database)",
    },
    {
        "step": 5,
        "name": "Memory Agent",
        "key": "memory",
        "role": "State Checkpointing & Organizational Memory Updates",
        "short_description": "Persists state context and maintains working agent memory.",
        "work_done": "Checkpointed working memory state, updated long-term organizational memory, and created state context summaries.",
        "output": "memory_context (saved to shared database)",
    },
    {
        "step": 6,
        "name": "Writer Agent",
        "key": "synthesize",
        "role": "Publication-Grade Report Synthesis",
        "short_description": "Synthesizes multi-section formal research reports from all database assets.",
        "work_done": "Synthesized an authoritative, multi-section deep research report from database state assets.",
        "output": "draft_report (saved to shared database)",
    },
    {
        "step": 7,
        "name": "Critic Agent",
        "key": "review",
        "role": "Quality Audit & Factuality Verification",
        "short_description": "Audits report draft against extracted claims and calculates quality scores.",
        "work_done": "Audited report draft for citation validity, factual accuracy, and assigned quality scores.",
        "output": "critique_score & critique_passed (saved to shared database)",
    },
    {
        "step": 8,
        "name": "Reflection Agent",
        "key": "reflection",
        "role": "Graph Routing & Quality Control Loop",
        "short_description": "Evaluates audit feedback and controls finalizing vs revision loops.",
        "work_done": "Evaluated quality score thresholds and decided whether to finalize or trigger a revision loop.",
        "output": "routing decision (finalize/revise)",
    },
]


def build_pipeline_system_prompt(agent_key: str, custom_instructions: str = "") -> str:
    """Build an architecturally aware system prompt for an agent in the 8-stage pipeline."""

    idx = next((i for i, a in enumerate(PIPELINE_AGENTS) if a["key"] == agent_key), 0)
    current = PIPELINE_AGENTS[idx]

    upstream = PIPELINE_AGENTS[:idx]
    downstream = PIPELINE_AGENTS[idx + 1 :]

    if upstream:
        upstream_str = f"THERE ARE {len(upstream)} AGENT(S) THAT EXECUTED BEFORE YOU IN THIS PIPELINE:\n" + "\n".join(
            f"  {i+1}. Step {a['step']}: {a['name']}\n"
            f"     - Role: {a['role']}\n"
            f"     - Description: {a['short_description']}\n"
            f"     - Work Completed: {a['work_done']}\n"
            f"     - Database Asset Produced: {a['output']}\n"
            for i, a in enumerate(upstream)
        )
    else:
        upstream_str = "THERE ARE 0 AGENTS BEFORE YOU. (You are the primary intake agent starting the pipeline)."

    if downstream:
        downstream_str = f"THERE ARE {len(downstream)} AGENT(S) THAT WILL EXECUTE AFTER YOU IN THIS PIPELINE:\n" + "\n".join(
            f"  {i+1}. Step {a['step']}: {a['name']}\n"
            f"     - Role: {a['role']}\n"
            f"     - Description: {a['short_description']}\n"
            f"     - Work They Will Execute: {a['work_done']}\n"
            f"     - Database Asset They Will Produce: {a['output']}\n"
            for i, a in enumerate(downstream)
        )
    else:
        downstream_str = "THERE ARE 0 AGENTS AFTER YOU. (You are the final evaluation engine delivering the research result)."

    return (
        f"YOU ARE THE {current['name'].upper()} (Step {current['step']} of 8 in the Autonomous Multi-Agent Research Platform).\n\n"
        f"CENTRAL ARCHITECTURE & SHARED DATABASE STORE:\n"
        f"All 8 agents execute sequentially over a central database state store. Every agent's output is persisted to the database in real time so subsequent agents can read and build upon it.\n\n"
        f"=========================================================\n"
        f"UPSTREAM AGENTS (BEFORE YOU):\n"
        f"=========================================================\n"
        f"{upstream_str}\n\n"
        f"=========================================================\n"
        f"YOUR SPECIFIC ROLE & RESPONSIBILITY (Step {current['step']}):\n"
        f"=========================================================\n"
        f"- Role: {current['role']}\n"
        f"- Description: {current['short_description']}\n"
        f"- You will write your output to the database as: {current['output']}.\n\n"
        f"=========================================================\n"
        f"DOWNSTREAM AGENTS (AFTER YOU):\n"
        f"=========================================================\n"
        f"{downstream_str}\n\n"
        f"=========================================================\n"
        f"SPECIFIC EXECUTION INSTRUCTIONS FOR THIS STEP:\n"
        f"=========================================================\n"
        f"{custom_instructions}"
    )


__all__ = ["PIPELINE_AGENTS", "build_pipeline_system_prompt"]
