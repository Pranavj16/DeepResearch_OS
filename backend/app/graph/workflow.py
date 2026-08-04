"""LangGraph workflow builder for the Autonomous Research Platform."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.graph.edges import route_after_review
from app.graph.nodes import ResearchGraphNodes
from app.graph.state import ResearchGraphState
from app.llm.router import LLMRouter


def build_research_graph(llm_router: LLMRouter):
    """Construct a versioned research StateGraph with checkpointing support."""

    nodes = ResearchGraphNodes(llm_router)
    builder = StateGraph(ResearchGraphState)

    builder.add_node("plan", nodes.plan_node)
    builder.add_node("search", nodes.search_node)
    builder.add_node("extract", nodes.extract_node)
    builder.add_node("knowledge", nodes.knowledge_node)
    builder.add_node("memory", nodes.memory_node)
    builder.add_node("synthesize", nodes.synthesize_node)
    builder.add_node("review", nodes.review_node)
    builder.add_node("reflection", nodes.reflection_node)
    builder.add_node("finalize", nodes.finalize_node)

    builder.add_edge(START, "plan")
    builder.add_edge("plan", "search")
    builder.add_edge("search", "extract")
    builder.add_edge("extract", "knowledge")
    builder.add_edge("knowledge", "memory")
    builder.add_edge("memory", "synthesize")
    builder.add_edge("synthesize", "review")
    builder.add_edge("review", "reflection")

    builder.add_conditional_edges(
        "reflection",
        route_after_review,
        {
            "finalize": "finalize",
            "synthesize": "synthesize",
        },
    )

    builder.add_edge("finalize", END)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


__all__ = ["build_research_graph"]
