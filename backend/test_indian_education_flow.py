import asyncio
import json
from app.graph.nodes import ResearchGraphNodes
from app.llm.router import LLMRouter

async def test_indian_education():
    router = LLMRouter()
    nodes = ResearchGraphNodes(router)
    
    topic = "Indian Education System: Analysis of National Education Policy (NEP 2020), Challenges and Modern Reforms"
    state = {
        "research_run_id": "run_indian_edu_2026",
        "objective": topic,
        "stage": "intake",
    }
    
    print("=" * 85)
    print("      BACKEND FASTAPI MULTI-AGENT EXECUTION FOR TOPIC")
    print(f"  Topic: {topic}")
    print("=" * 85)
    
    # 1. Execute Nodes
    p_res = await nodes.plan_node(state)
    state.update(p_res)
    
    s_res = await nodes.search_node(state)
    state.update(s_res)
    
    e_res = await nodes.extract_node(state)
    state.update(e_res)
    
    k_res = await nodes.knowledge_node(state)
    state.update(k_res)
    
    m_res = await nodes.memory_node(state)
    state.update(m_res)
    
    w_res = await nodes.synthesize_node(state)
    state.update(w_res)
    
    c_res = await nodes.review_node(state)
    state.update(c_res)
    
    r_res = await nodes.reflection_node(state)
    state.update(r_res)

    # 2. Construct Backend Payload (Saved to DB as run.details and run.result_summary)
    backend_payload = {
        "status": "completed",
        "stage": state.get("stage", "reflection"),
        "result_summary": state.get("draft_report", ""),
        "details": {
            "plan_steps": state.get("plan_steps", []),
            "sources": state.get("sources", []),
            "claims": state.get("claims", []),
            "critique_score": state.get("critique_score", 0.9),
            "critique_passed": state.get("critique_passed", True),
            "draft_report": state.get("draft_report", ""),
        }
    }

    print("\n[BACKEND API OUTPUT PAYLOAD (FastAPI -> PostgreSQL)]")
    print(f"  - Status: {backend_payload['status']}")
    print(f"  - Stage: {backend_payload['stage']}")
    print(f"  - Plan Steps Count: {len(backend_payload['details']['plan_steps'])}")
    print(f"  - Crawled Sources Count: {len(backend_payload['details']['sources'])}")
    print(f"  - Extracted Claims Count: {len(backend_payload['details']['claims'])}")
    print(f"  - Report Length: {len(backend_payload['details']['draft_report'])} characters")

    print("\n[CRAWLED SOURCES RETURNED BY SEARCH AGENT]:")
    for idx, src in enumerate(backend_payload['details']['sources'][:4], 1):
        print(f"  {idx}. Title: {src.get('title')}")
        print(f"     URL:   {src.get('url')}")

    print("\n[EXTRACTED CLAIMS RETURNED BY EXTRACTOR AGENT]:")
    for idx, claim in enumerate(backend_payload['details']['claims'][:3], 1):
        print(f"  {idx}. {claim[:120]}...")

    print("\n" + "=" * 85)
    print("      FRONTEND DISPLAY MAPPING (Django UI -> User Interface)")
    print("=" * 85)
    print("1. Dashboard Screen (/):")
    print(f"   - Run Card Title: '{topic[:45]}...'")
    print("   - Status Tag: COMPLETED (Green Badge)")
    print("   - Quick Actions: View Report, Export PDF, Delete")
    print("\n2. Report Detail Screen (/research/report/<run_id>):")
    print("   - Main Canvas: 7-Section Markdown Document rendered via Marked.js:")
    print("     * Executive Summary")
    print("     * Background & Domain Context")
    print("     * Key Research Findings")
    print("     * Detailed Technical Analysis")
    print("     * Strategic Recommendations & Action Plan")
    print("     * Verified Sources & References")
    print("   - Right Sidebar Component 1 (Verified Claims):")
    for idx, claim in enumerate(backend_payload['details']['claims'][:2], 1):
        print(f"     * Card #{idx}: Confidence 0.98 | {claim[:80]}...")
    print("   - Right Sidebar Component 2 (Primary Web Sources):")
    for idx, src in enumerate(backend_payload['details']['sources'][:2], 1):
        print(f"     * Source #{idx}: {src.get('title')} ({src.get('url')})")

    print("\n3. Knowledge Base Screen (/research/knowledge):")
    print("   - Document Browser Tab: Displays completed research run card.")
    print("   - Web Source Explorer Tab: Displays all crawled URLs with multi-engine crawl badges.")
    print("   - Citation Index Tab: Displays extracted factual claim spans with verification scores.")

if __name__ == "__main__":
    asyncio.run(test_indian_education())
