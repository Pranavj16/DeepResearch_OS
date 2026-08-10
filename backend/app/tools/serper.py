"""Google Serper API search adapter for deep web search."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ConfigDict, SecretStr

from app.core.settings import Settings
from app.schemas.search import SearchResult


class _SerperOrganicResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str
    link: str
    snippet: str = ""
    date: str | None = None


class SerperSearchClient:
    """Execute Google Serper Search API requests."""

    def __init__(
        self,
        *,
        api_key: SecretStr,
        timeout_seconds: float = 15.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._api_url = "https://google.serper.dev/search"
        self._http_client = http_client or httpx.AsyncClient(timeout=timeout_seconds)

    @classmethod
    def from_settings(cls, settings: Settings) -> SerperSearchClient | None:
        key = settings.serper_api_key
        if not key:
            return None
        return cls(api_key=SecretStr(key))

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        if not self._api_key.get_secret_value():
            return []

        try:
            res = await self._http_client.post(
                self._api_url,
                headers={"X-API-KEY": self._api_key.get_secret_value(), "Content-Type": "application/json"},
                json={"q": query, "num": max_results},
            )
            res.raise_for_status()
            data = res.json()
            organic = data.get("organic", [])
            results = []
            for item in organic[:max_results]:
                results.append(
                    SearchResult(
                        title=item.get("title", "Google Result"),
                        url=item.get("link", "https://google.com"),
                        content=item.get("snippet", ""),
                        score=0.92,
                        published_date=item.get("date", "2026"),
                    )
                )
            return results
        except Exception:
            return []
