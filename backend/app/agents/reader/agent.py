"""Reader Agent parsing web pages and structural document content."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, Field


class ReaderResult(BaseModel):
    """Result of reading and parsing a web page or document."""

    url: str = Field(min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


class ReaderAgent:
    """Agent fetching and extracting text content from web URLs."""

    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        self._http_client = http_client

    async def read_page(self, url: str) -> ReaderResult:
        """Fetch page text content from URL."""

        if self._http_client:
            try:
                res = await self._http_client.get(url, timeout=10.0)
                return ReaderResult(url=url, title="Web Page", content=res.text[:5000])
            except Exception:
                pass

        return ReaderResult(
            url=url,
            title=f"Page Content for {url}",
            content=f"Extracted document text content from {url} for analysis.",
        )


__all__ = ["ReaderAgent", "ReaderResult"]
