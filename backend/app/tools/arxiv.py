"""ArXiv Academic Research Paper API Search Adapter."""

from __future__ import annotations

import xml.etree.ElementTree as ET
import httpx
from pydantic import SecretStr

from app.core.settings import Settings
from app.schemas.search import SearchResult


class ArxivSearchClient:
    """Execute ArXiv academic paper API searches."""

    def __init__(self, api_key: SecretStr | None = None, timeout_seconds: float = 15.0) -> None:
        self._api_key = api_key
        self._api_url = "http://export.arxiv.org/api/query"
        self._timeout_seconds = timeout_seconds

    @classmethod
    def from_settings(cls, settings: Settings) -> ArxivSearchClient:
        key = settings.arxiv_api_key
        return cls(api_key=SecretStr(key) if key else None)

    async def search(self, query: str, max_results: int = 4) -> list[SearchResult]:
        try:
            headers = {}
            if self._api_key and self._api_key.get_secret_value():
                headers["Authorization"] = f"Bearer {self._api_key.get_secret_value()}"

            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                res = await client.get(
                    self._api_url,
                    headers=headers,
                    params={
                        "search_query": f"all:{query}",
                        "start": 0,
                        "max_results": max_results,
                    },
                )
                res.raise_for_status()

            root = ET.fromstring(res.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            results = []
            for entry in root.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                summary_elem = entry.find("atom:summary", ns)
                id_elem = entry.find("atom:id", ns)

                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None and title_elem.text else "ArXiv Paper"
                summary = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None and summary_elem.text else ""
                url = id_elem.text.strip() if id_elem is not None and id_elem.text else "https://arxiv.org"

                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        content=summary[:400] + "..." if len(summary) > 400 else summary,
                        score=0.95,
                        published_date="2026",
                    )
                )
            return results
        except Exception:
            return []
