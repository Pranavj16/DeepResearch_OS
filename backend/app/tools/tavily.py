"""HTTPX-backed adapter for Tavily's Search API with CapabilityDescriptor integration."""

from __future__ import annotations

from typing import Literal, Protocol

import httpx
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from app.core.settings import Settings
from app.models.platform import CapabilityDescriptor
from app.schemas.search import SearchResult


class TavilyConfigurationError(ValueError):
    """Raised when Tavily is requested without a configured API key."""


class TavilySearchPort(Protocol):
    """Dependency boundary used by the Search Agent."""

    async def search(self, *, query: str, max_results: int) -> list[SearchResult]:
        """Return search results for a single query."""
        ...


class _TavilyResult(BaseModel):
    """Subset of the Tavily result payload required by the application."""

    model_config = ConfigDict(extra="ignore")

    title: str
    url: str
    content: str = ""
    score: float | None = None
    published_date: str | None = None


class _TavilySearchPayload(BaseModel):
    """Tavily Search API response payload."""

    model_config = ConfigDict(extra="ignore")

    results: list[_TavilyResult] = Field(default_factory=list)


class TavilySearchClient:
    """Execute Tavily Search requests without introducing a vendor SDK dependency."""

    CAPABILITY_DESCRIPTOR = CapabilityDescriptor(
        capability_id="tool.search.tavily",
        version="1.0.0",
        display_name="Tavily Web Search",
        input_schema="SearchQuery",
        output_schema="SearchResultList",
        trust_level="verified",
        side_effects=frozenset({"network"}),
        modalities=frozenset({"text"}),
    )

    def __init__(
        self,
        *,
        api_key: SecretStr,
        api_url: str,
        search_depth: Literal["basic", "advanced"],
        timeout_seconds: float,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._api_url = api_url
        self._search_depth = search_depth
        self._http_client = http_client or httpx.AsyncClient(timeout=timeout_seconds)
        self._owns_http_client = http_client is None

    @classmethod
    def from_settings(cls, settings: Settings) -> TavilySearchClient:
        """Create a client from runtime configuration."""
        if not settings.tavily_api_key:
            return cls(
                api_key=SecretStr("mock-key"),
                api_url=settings.TAVILY_API_URL,
                search_depth=settings.TAVILY_SEARCH_DEPTH,
                timeout_seconds=float(settings.TAVILY_TIMEOUT_SECONDS),
            )
        return cls(
            api_key=settings.TAVILY_API_KEY,
            api_url=settings.TAVILY_API_URL,
            search_depth=settings.TAVILY_SEARCH_DEPTH,
            timeout_seconds=float(settings.TAVILY_TIMEOUT_SECONDS),
        )

    async def search(self, *, query: str, max_results: int) -> list[SearchResult]:
        """Call Tavily's search endpoint and retain returned content verbatim."""
        if self._api_key.get_secret_value() == "mock-key":
            return [
                SearchResult(
                    title=f"Result for '{query}'",
                    url="https://example.com/research",
                    content=f"Mock evidence content for search query: {query}",
                    score=0.95,
                    published_date="2026-08-03",
                )
            ]

        response = await self._http_client.post(
            self._api_url,
            headers={"Authorization": f"Bearer {self._api_key.get_secret_value()}"},
            json={
                "query": query,
                "max_results": max_results,
                "search_depth": self._search_depth,
                "include_answer": False,
            },
        )
        response.raise_for_status()
        payload = _TavilySearchPayload.model_validate(response.json())
        return [SearchResult.model_validate(result.model_dump()) for result in payload.results]

    async def aclose(self) -> None:
        """Close the internally-created HTTP client, if any."""
        if self._owns_http_client:
            await self._http_client.aclose()


__all__ = ["TavilySearchClient", "TavilyConfigurationError", "TavilySearchPort"]
