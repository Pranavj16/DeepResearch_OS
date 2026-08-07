"""HTTP download and readable-text extraction for web pages."""

from __future__ import annotations

from html.parser import HTMLParser
from typing import Protocol

import httpx
from pydantic import BaseModel


class DownloadedPage(BaseModel):
    """Readable page material downloaded from a URL."""

    url: str
    title: str | None = None
    content: str


class PageDownloader(Protocol):
    """Boundary for downloading a page's readable content."""

    async def download(self, url: str) -> DownloadedPage:
        """Download and extract visible text from a URL."""
        ...


class _ReadableTextParser(HTMLParser):
    """Extract visible text while excluding non-readable HTML elements."""

    _SKIPPED_TAGS = {"script", "style", "noscript", "svg", "template", "head"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._title_parts: list[str] = []
        self._text_parts: list[str] = []
        self._skip_depth = 0
        self._inside_title = False

    @property
    def title(self) -> str | None:
        """Return normalized document title, when present."""
        title = " ".join("".join(self._title_parts).split())
        return title or None

    @property
    def content(self) -> str:
        """Return normalized visible document text."""
        return " ".join("".join(self._text_parts).split())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Track elements whose text should not be included."""
        del attrs
        normalized_tag = tag.lower()
        if normalized_tag in self._SKIPPED_TAGS:
            self._skip_depth += 1
        if normalized_tag == "title":
            self._inside_title = True

    def handle_endtag(self, tag: str) -> None:
        """Leave excluded elements and the title element."""
        normalized_tag = tag.lower()
        if normalized_tag in self._SKIPPED_TAGS and self._skip_depth:
            self._skip_depth -= 1
        if normalized_tag == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        """Record text nodes that are visible to a page reader."""
        if self._inside_title:
            self._title_parts.append(data)
        if not self._skip_depth:
            self._text_parts.append(data)


def extract_readable_content(html: str) -> tuple[str | None, str]:
    """Extract a page title and normalized visible text from HTML using BeautifulSoup4."""
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        for element in soup(["script", "style", "noscript", "svg", "template", "head", "iframe", "footer", "nav"]):
            element.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else None
        content = " ".join(soup.get_text(separator=" ", strip=True).split())
        return title, content
    except Exception:
        parser = _ReadableTextParser()
        parser.feed(html)
        parser.close()
        return parser.title, parser.content


class HttpxPageDownloader:
    """Page downloader backed by an injected or internally-managed HTTPX client."""

    def __init__(
        self,
        *,
        timeout_seconds: float,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._http_client = http_client or httpx.AsyncClient(
            timeout=timeout_seconds,
            follow_redirects=True,
        )
        self._owns_http_client = http_client is None

    async def download(self, url: str) -> DownloadedPage:
        """Download one HTML page and extract its readable text."""
        response = await self._http_client.get(url)
        response.raise_for_status()
        title, content = extract_readable_content(response.text)
        return DownloadedPage(url=str(response.url), title=title, content=content)

    async def aclose(self) -> None:
        """Close the internally-created HTTPX client, if one is owned."""
        if self._owns_http_client:
            await self._http_client.aclose()
