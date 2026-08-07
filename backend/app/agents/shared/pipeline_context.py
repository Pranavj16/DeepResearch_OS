"""Central Multi-Agent Pipeline Context & Architectural System Prompt Builder."""

from __future__ import annotations

from typing import Any

PIPELINE_AGENTS: list[dict[str, Any]] = [
    {
        "step": 1,
        "name": "Planner Agent",
        "key": "plan",
        "role": "Decomposes research objective into logical sub-goals, search queries, and execution strategy steps.",
        "output": "plan_steps (saved to shared database)",
    },
    {
        "step": 2,
        "name": "Searcher Agent",
        "key": "search",
        "role": "Executes live web search and academic paper crawling matching the planner's sub-goals.",
        "output": "sources (saved to shared database)",
    },
    {
        "step": 3,
        "name": "Extractor / Reader Agent",
        "key": "extract",
        "role": "Parses raw web pages & literature from the database and extracts verified factual claim spans.",
        "output": "claims (saved to shared database)",
    },
    {
        "step": 4,
        "name": "Knowledge Agent",
        "key": "knowledge",
        "role": "Constructs entity-claim relationships, RAG vector indices, and knowledge graph objects in the database.",
        "output": "knowledge_objects (saved to shared database)",
    },
    {
        "step": 5,
        "name": "Memory Agent",
        "key": "memory",
        "role": "Checkpoints working memory state, updates long-term organizational memory, and creates persistent state summaries.",
        "output": "memory_context (saved to shared database)",
    },
    {
        "step": 6,
        "name": "Writer Agent",
        "key": "synthesize",
        "role": "Reads all database state assets from steps 1-5 and synthesizes a world-class, multi-section research report.",
        "output": "draft_report (saved to shared database)",
    },
    {
        "step": 7,
        "name": "Critic Agent",
        "key": "review",
        "role": "Audits the draft report against database claims & sources, checking for hallucinations and citation accuracy.",
        "output": "critique_score & critique_passed (saved to shared database)",
    },
    {
        "step": 8,
        "name": "Reflection Agent",
        "key": "reflection",
        "role": "Evaluates audit score and controls graph routing (finalize vs loop revision).",
        "output": "routing decision (finalize/revise)",
    },
]


def build_pipeline_system_prompt(agent_key: str, custom_instructions: str = "") -> str:
    """Build an architecturally aware system prompt for an agent in the 8-stage pipeline."""

    idx = next((i for i, a in enumerate(PIPELINE_AGENTS) if a["key"] == agent_key), 0)
    current = PIPELINE_AGENTS[idx]

    upstream = PIPELINE_AGENTS[:idx]
    downstream = PIPELINE_AGENTS[idx + 1 :]

    upstream_str = (
        "\n".join(
            f"  - Step {a['step']}: {a['name']} ({a['role']}) -> Produced: {a['output']}"
            for a in upstream
        )
        if upstream
        else "  - None (You are the primary intake agent starting the workflow)."
    )

    downstream_str = (
        "\n".join(
            f"  - Step {a['step']}: {a['name']} ({a['role']}) -> Will consume your output to generate: {a['output']}"
            for a in downstream
        )
        if downstream
        else "  - None (You are the final evaluation engine delivering the result)."
    )

    return (
        f"YOU ARE THE {current['name'].upper()} (Step {current['step']} of 8 in the Autonomous Multi-Agent Research Platform).\n\n"
        f"CENTRAL ARCHITECTURE & SHARED DATABASE STORE:\n"
        f"All 8 agents execute sequentially over a central database state store. Every agent's output is persisted to the database in real time so subsequent agents can read and build upon it.\n\n"
        f"UPSTREAM AGENTS THAT EXECUTED BEFORE YOU (Their outputs are stored in the database for you):\n"
        f"{upstream_str}\n\n"
        f"YOUR SPECIFIC ROLE & RESPONSIBILITY (Step {current['step']}):\n"
        f"{current['role']}\n"
        f"You will write your output to the database as: {current['output']}.\n\n"
        f"DOWNSTREAM AGENTS THAT EXECUTE AFTER YOU (They will read your database output):\n"
        f"{downstream_str}\n\n"
        f"SPECIFIC EXECUTION INSTRUCTIONS:\n"
        f"{custom_instructions}"
    )


__all__ = ["PIPELINE_AGENTS", "build_pipeline_system_prompt"]
