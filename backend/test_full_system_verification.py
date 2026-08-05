import asyncio
from app.graph.nodes import ResearchGraphNodes
from app.llm.router import LLMRouter

async def verify_full_system():
    router = LLMRouter()
    nodes = ResearchGraphNodes(router)
    
    test_topic = "Impact of Quantum Computing on Modern Cryptography and RSA Encryption Security"
    state = {
        "research_run_id": "test_quantum_crypto_2026",
        "objective": test_topic,
        "stage": "intake",
    }
    
    print("=" * 85)
    print("              FULL SYSTEM MULTI-AGENT VERIFICATION & AUDIT")
    print(f"  Input Topic: {test_topic}")
    print("=" * 85)
    
    # 1. PLANNER AGENT
    print("\n[AGENT 1/8] PLANNER AGENT (OpenRouter)")
    p_res = await nodes.plan_node(state)
    state.update(p_res)
    print(f"  -> Stage: {state.get('stage')}")
    print(f"  -> Generated Strategy Steps ({len(state.get('plan_steps', []))}):")
    for step in state.get("plan_steps", []):
        print(f"     * {step}")
    assert any("Quantum" in s or "Cryptography" in s or "RSA" in s for s in state.get("plan_steps", [])), "Planner output lost topic alignment!"

    # 2. SEARCH AGENT
    print("\n[AGENT 2/8] SEARCH AGENT (Tavily & Google Serper & DuckDuckGo)")
    s_res = await nodes.search_node(state)
    state.update(s_res)
    print(f"  -> Search Queries Used: '{state.get('search_query_used')}'")
    sources = state.get("sources", [])
    print(f"  -> Crawled Sources Count: {len(sources)}")
    for idx, src in enumerate(sources[:3], 1):
        print(f"     [{idx}] {src['title']} ({src['url']})")
    assert len(sources) > 0, "Search Agent failed to crawl sources!"
    assert any("quantum" in s['content'].lower() or "crypt" in s['content'].lower() or "rsa" in s['content'].lower() for s in sources), "Search Agent sources unrelated to topic!"

    # 3. EXTRACTOR AGENT
    print("\n[AGENT 3/8] EXTRACTOR AGENT (NVIDIA NIM)")
    e_res = await nodes.extract_node(state)
    state.update(e_res)
    claims = state.get("claims", [])
    print(f"  -> Extracted Factual Claims Count: {len(claims)}")
    for idx, claim in enumerate(claims[:3], 1):
        print(f"     Claim #{idx}: {claim[:130]}...")
    assert len(claims) > 0, "Extractor Agent produced no claims!"
    assert any("quantum" in c.lower() or "crypt" in c.lower() or "rsa" in c.lower() for c in claims), "Extractor Agent claims unrelated to topic!"

    # 4. KNOWLEDGE AGENT
    print("\n[AGENT 4/8] KNOWLEDGE AGENT (Groq LPU)")
    k_res = await nodes.knowledge_node(state)
    state.update(k_res)
    k_objs = state.get("knowledge_objects", [])
    print(f"  -> Deduplicated Knowledge Objects: {len(k_objs)}")
    assert len(k_objs) > 0, "Knowledge Agent produced no knowledge objects!"

    # 5. MEMORY AGENT
    print("\n[AGENT 5/8] MEMORY AGENT (Groq LPU)")
    m_res = await nodes.memory_node(state)
    state.update(m_res)
    mem_ctx = state.get("memory_context")
    print(f"  -> Memory Context Saved: {mem_ctx}")
    assert mem_ctx is not None, "Memory Agent context failed!"

    # 6. WRITER AGENT
    print("\n[AGENT 6/8] WRITER AGENT (Google Gemini)")
    w_res = await nodes.synthesize_node(state)
    state.update(w_res)
    report = state.get("draft_report", "")
    print(f"  -> Report Synthesized Length: {len(report)} characters")
    assert "Quantum" in report or "Cryptography" in report or "RSA" in report, "Writer Agent report body lost topic alignment!"

    # 7. CRITIC AGENT
    print("\n[AGENT 7/8] CRITIC AGENT (Google Gemini)")
    r_res = await nodes.review_node(state)
    state.update(r_res)
    score = state.get("critique_score")
    passed = state.get("critique_passed")
    print(f"  -> Audit Score: {score} / 1.00")
    print(f"  -> Audit Status: {'PASSED [OK]' if passed else 'FAILED'}")
    assert score is not None and score >= 0.7, "Critic Agent audit score too low!"

    # 8. REFLECTION AGENT
    print("\n[AGENT 8/8] REFLECTION AGENT (Google Gemini)")
    rf_res = await nodes.reflection_node(state)
    state.update(rf_res)
    print(f"  -> Execution State Finalized: {state.get('stage')}")

    print("\n" + "=" * 85)
    print("                 FINAL SYNTHESIZED RESEARCH REPORT OUTPUT")
    print("=" * 85)
    print(report)
    print("=" * 85)

if __name__ == "__main__":
    asyncio.run(verify_full_system())
