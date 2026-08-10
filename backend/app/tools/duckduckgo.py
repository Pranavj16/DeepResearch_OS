"""DuckDuckGo AI Web Search Adapter (Free, zero API key requirement)."""

from __future__ import annotations

import re
import urllib.parse

import httpx

from app.schemas.search import SearchResult


class DuckDuckGoSearchClient:
    """Execute DuckDuckGo HTML web search queries using standard library parsing."""

    def __init__(self, timeout_seconds: float = 10.0) -> None:
        self._search_url = "https://html.duckduckgo.com/html/"
        self._timeout_seconds = timeout_seconds

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds, follow_redirects=True) as client:
                res = await client.post(self._search_url, data={"q": query}, headers=headers)
                res.raise_for_status()

            html = res.text
            # Regex parse result blocks from DuckDuckGo HTML
            pattern = re.compile(
                r'<a[^>]+class="result__url"[^>]+href="([^"]+)"[^>]*>\s*(.*?)\s*</a>.*?'
                r'<a[^>]+class="result__snippet"[^>]*>\s*(.*?)\s*</a>',
                re.DOTALL | re.IGNORECASE,
            )
            matches = pattern.findall(html)
            results = []

            if not matches:
                # Secondary fallback pattern for title & snippet
                pattern2 = re.compile(
                    r'<a[^>]+class="result__title"[^>]*>(.*?)</a>.*?'
                    r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
                    re.DOTALL | re.IGNORECASE,
                )
                matches2 = pattern2.findall(html)
                for item in matches2[:max_results]:
                    raw_title, raw_snippet = item
                    title = re.sub(r"<[^>]+>", "", raw_title).strip()
                    snippet = re.sub(r"<[^>]+>", "", raw_snippet).strip()
                    results.append(
                        SearchResult(
                            title=title or f"DuckDuckGo Result: {query}",
                            url=f"https://duckduckgo.com/?q={urllib.parse.quote(query)}",
                            content=snippet,
                            score=0.88,
                            published_date="2026",
                        )
                    )
                return results

            for match in matches[:max_results]:
                raw_url, raw_title, raw_snippet = match
                title = re.sub(r"<[^>]+>", "", raw_title).strip()
                snippet = re.sub(r"<[^>]+>", "", raw_snippet).strip()
                clean_url = raw_url.strip()
                if "uddg=" in clean_url:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(clean_url).query)
                    clean_url = parsed.get("uddg", [clean_url])[0]

                results.append(
                    SearchResult(
                        title=title or "Web Evidence Source",
                        url=clean_url if clean_url.startswith("http") else f"https://{clean_url}",
                        content=snippet,
                        score=0.88,
                        published_date="2026",
                    )
                )
            return results
        except Exception:
            return []
