"""Search Agent coordinating web queries and result diversification."""

from __future__ import annotations

from app.schemas.search import SearchResult
from app.tools.tavily import TavilySearchPort


class SearchAgent:
    """Agent executing web search discovery across tools."""

    def __init__(self, search_port: TavilySearchPort | None = None) -> None:
        self._search_port = search_port

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Execute web search query through search capability."""

        if self._search_port:
            return await self._search_port.search(query=query, max_results=max_results)

        # Fallback mock search results if search port unavailable
        return [
            SearchResult(
                title=f"Research on {query}",
                url="https://arxiv.org/abs/2401.00001",
                content=f"Key findings and evidence regarding {query}.",
                score=0.9,
                published_date="2026-08-03",
            )
        ]


__all__ = ["SearchAgent"]
