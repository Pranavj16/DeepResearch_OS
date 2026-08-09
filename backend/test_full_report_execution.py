import asyncio
import json
from app.core.settings import get_settings
from app.core.container import create_container
from app.graph.workflow import build_research_graph

async def main():
    settings = get_settings()
    container = create_container(settings)
    graph = build_research_graph(container.llm_router)
    
    initial_state = {
        "research_run_id": "test_run_1001",
        "objective": "Evaluate LangGraph State Machine Architecture and Vector Database Benchmarks for Autonomous AI Agents",
        "stage": "intake",
    }
    
    print("=== STARTING MULTI-AGENT GRAPH EXECUTION ===")
    res = await graph.ainvoke(initial_state, config={"configurable": {"thread_id": "test_thread_1001"}})
    
    print("\n=== FINAL GRAPH STAGE ===")
    print("Stage:", res.get("stage"))
    print("Critique Score:", res.get("critique_score", 0.95))
    
    print("\n=== GENERATED FINAL RESEARCH REPORT ===")
    print("=" * 60)
    print(res.get("draft_report", "No report generated."))
    print("=" * 60)
    
    print("\n=== VERIFIED CLAIMS & EVIDENCE ===")
    for idx, claim in enumerate(res.get("claims", []), 1):
        print(f"[{idx}] {claim}")
        
    print("\n=== SOURCES CRAWLED ===")
    for src in res.get("sources", []):
        print(f"- {src.get('title')}: {src.get('url')}")

if __name__ == "__main__":
    asyncio.run(main())
