import asyncio
from app.graph.nodes import ResearchGraphNodes
from app.llm.router import LLMRouter

async def run_topic_research():
    router = LLMRouter()
    nodes = ResearchGraphNodes(router)
    
    topic = "Future of Autonomous Multi-Agent AI Systems with Vector Memory & LangGraph State Persistence"
    state = {
        "research_run_id": "run_topic_2026_08_05",
        "objective": topic,
        "stage": "intake",
    }
    
    print("=" * 80)
    print(f"       AUTONOMOUS MULTI-AGENT RESEARCH TASK EXECUTION")
    print(f"       Topic: {topic}")
    print("=" * 80)
    
    # 1. Planner Agent (OpenRouter)
    print("\n[STEP 1] PLANNER AGENT (OpenRouter: meta-llama/llama-3.3-70b-instruct)")
    p_res = await nodes.plan_node(state)
    state.update(p_res)
    for step in state.get("plan_steps", []):
        print(f"   -> {step}")

    # 2. Search Agent (Tavily)
    print("\n[STEP 2] SEARCH AGENT (Tavily Search API)")
    s_res = await nodes.search_node(state)
    state.update(s_res)
    print(f"   -> Query Executed: '{state.get('search_query_used')}'")
    for src in state.get("sources", []):
        print(f"   -> Found Source: {src['title']} ({src['url']})")

    # 3. Extractor Agent (NVIDIA NIM)
    print("\n[STEP 3] EXTRACTOR AGENT (NVIDIA NIM: z-ai/glm-5.2)")
    e_res = await nodes.extract_node(state)
    state.update(e_res)
    for claim in state.get("claims", []):
        print(f"   -> Extracted Claim: {claim[:120]}...")

    # 4. Knowledge Agent (Groq LPU)
    print("\n[STEP 4] KNOWLEDGE AGENT (Groq LPU: llama-3.3-70b-versatile)")
    k_res = await nodes.knowledge_node(state)
    state.update(k_res)
    print(f"   -> Knowledge Entities Deduplicated & Projected: {len(state.get('knowledge_objects', []))}")

    # 5. Memory Agent (Groq LPU)
    print("\n[STEP 5] MEMORY AGENT (Groq LPU: llama-3.3-70b-versatile)")
    m_res = await nodes.memory_node(state)
    state.update(m_res)
    print(f"   -> State Checkpointed: {state.get('memory_context')}")

    # 6. Writer Agent (Google Gemini)
    print("\n[STEP 6] WRITER AGENT (Google Gemini: gemini-2.5-flash)")
    w_res = await nodes.synthesize_node(state)
    state.update(w_res)
    print("   -> Formal Research Report Synthesized!")

    # 7. Critic Agent (Google Gemini)
    print("\n[STEP 7] CRITIC AGENT (Google Gemini: gemini-2.5-flash)")
    r_res = await nodes.review_node(state)
    state.update(r_res)
    print(f"   -> Quality Score Assigned: {state.get('critique_score')} / 1.00")
    print(f"   -> Audit Status: {'PASSED' if state.get('critique_passed') else 'REVISION REQUIRED'}")

    # 8. Reflection Agent (Google Gemini)
    print("\n[STEP 8] REFLECTION AGENT (Google Gemini: gemini-2.5-flash)")
    rf_res = await nodes.reflection_node(state)
    state.update(rf_res)
    print("   -> Execution Finalized & Locked.")

    print("\n" + "=" * 80)
    print("                    FINAL SYNTHESIZED RESEARCH REPORT")
    print("=" * 80)
    print(state.get("draft_report"))
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_topic_research())
