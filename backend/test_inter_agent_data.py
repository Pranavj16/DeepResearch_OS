import asyncio
from app.graph.nodes import ResearchGraphNodes
from app.llm.router import LLMRouter

async def test_data_sharing():
    router = LLMRouter()
    nodes = ResearchGraphNodes(router)
    
    state = {
        "research_run_id": "test_context_run_2002",
        "objective": "Design and Benchmark Next-Gen Autonomous AI Agents with LangGraph & Multi-Provider LLMs",
    }
    
    print("=" * 70)
    print("      INTER-AGENT DATA SHARING & COMMUNICATION FLOW VERIFICATION")
    print("=" * 70)
    
    # 1. Planner
    p_res = await nodes.plan_node(state)
    state.update(p_res)
    print("\n[1] PLANNER AGENT (OpenRouter):")
    print("    - Generated Plan Steps:", state.get("plan_steps"))
    print("    - Search Queries Produced:", state.get("queries"))
    
    # 2. Searcher
    s_res = await nodes.search_node(state)
    state.update(s_res)
    print("\n[2] SEARCH AGENT (Tavily Search):")
    print("    - Search Query Received from Planner:", state.get("search_query_used"))
    print("    - Crawled Sources Count:", len(state.get("sources", [])))
    
    # 3. Extractor
    e_res = await nodes.extract_node(state)
    state.update(e_res)
    print("\n[3] EXTRACTOR AGENT (NVIDIA NIM):")
    print("    - Claims Extracted from Sources & Plan:", state.get("claims"))
    
    # 4. Knowledge
    k_res = await nodes.knowledge_node(state)
    state.update(k_res)
    print("\n[4] KNOWLEDGE AGENT (Groq LPU):")
    print("    - Knowledge Objects Created:", len(state.get("knowledge_objects", [])))
    
    # 5. Memory
    m_res = await nodes.memory_node(state)
    state.update(m_res)
    print("\n[5] MEMORY AGENT (Groq LPU):")
    print("    - Memory Context Saved:", state.get("memory_context"))
    
    # 6. Writer
    w_res = await nodes.synthesize_node(state)
    state.update(w_res)
    print("\n[6] WRITER AGENT (Google Gemini):")
    print("    - Synthesized Final Report Draft Received Output from all 5 preceding agents!")
    
    # 7. Critic
    r_res = await nodes.review_node(state)
    state.update(r_res)
    print("\n[7] CRITIC AGENT (Google Gemini):")
    print("    - Audit Quality Score:", state.get("critique_score"))
    print("    - Audit Passed:", state.get("critique_passed"))

    print("\n" + "=" * 70)
    print("                       FINAL GENERATED REPORT")
    print("=" * 70)
    print(state.get("draft_report"))
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_data_sharing())
