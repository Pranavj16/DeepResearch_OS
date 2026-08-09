import asyncio
from app.graph.nodes import ResearchGraphNodes
from app.llm.router import LLMRouter

async def test_direct():
    router = LLMRouter()
    nodes = ResearchGraphNodes(router)
    
    state = {
        "research_run_id": "test_1001",
        "objective": "Evaluate LangGraph State Machine Architecture and Vector Database Benchmarks for Autonomous AI Agents",
    }
    
    # 1. Plan
    p_res = await nodes.plan_node(state)
    state.update(p_res)
    print("[+] STAGE 1 (Planner - OpenRouter):", state.get("stage"), "| Provider:", state.get("provider"))
    
    # 2. Search
    s_res = await nodes.search_node(state)
    state.update(s_res)
    print("[+] STAGE 2 (Searcher - Tavily):", state.get("stage"), "| Sources count:", len(state.get("sources", [])))
    
    # 3. Extract
    e_res = await nodes.extract_node(state)
    state.update(e_res)
    print("[+] STAGE 3 (Extractor - NVIDIA):", state.get("stage"), "| Claims count:", len(state.get("claims", [])))
    
    # 4. Knowledge
    k_res = await nodes.knowledge_node(state)
    state.update(k_res)
    print("[+] STAGE 4 (Knowledge - Groq):", state.get("stage"), "| Provider:", state.get("provider"))
    
    # 5. Memory
    m_res = await nodes.memory_node(state)
    state.update(m_res)
    print("[+] STAGE 5 (Memory - Groq):", state.get("stage"), "| Provider:", state.get("provider"))
    
    # 6. Synthesize / Write
    w_res = await nodes.synthesize_node(state)
    state.update(w_res)
    print("[+] STAGE 6 (Writer - Gemini):", state.get("stage"), "| Provider:", state.get("provider"))
    
    # 7. Review / Critic
    r_res = await nodes.review_node(state)
    state.update(r_res)
    print("[+] STAGE 7 (Critic - Gemini):", state.get("stage"), "| Critique Score:", state.get("critique_score"))
    
    print("\n" + "="*70)
    print("                 GENERATED FINAL RESEARCH REPORT")
    print("="*70)
    print(state.get("draft_report"))
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_direct())
