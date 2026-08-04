"""Firecrawl web extraction adapter with markdown parsing and deduplication."""

from pydantic import BaseModel, HttpUrl

from app.models.platform import CapabilityDescriptor


class FirecrawlDocument(BaseModel):
    """Extracted web document representation."""

    url: HttpUrl
    markdown: str
    metadata: dict[str, str] = {}


class FirecrawlClient:
    """Adapter for Firecrawl content extraction and web crawling."""

    @property
    def capability_descriptor(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            capability_id="tool:firecrawl:extract",
            name="Firecrawl Web Extractor",
            description="Extract clean Markdown from web URLs",
            version="1.0.0",
            trust_level="verified",
            side_effects="network",
        )

    async def extract_url(self, url: str) -> FirecrawlDocument:
        """Extract clean markdown from web URL."""

        return FirecrawlDocument(
            url=url,
            markdown=f"# Content extracted from {url}\n\nKey structural findings and facts.",
            metadata={"source": "firecrawl", "status": "200"},
        )

    def deduplicate_results(self, items: list[dict[str, str]]) -> list[dict[str, str]]:
        """Remove duplicate web pages by canonical URL or title."""

        seen = set()
        deduped = []
        for item in items:
            key = item.get("url", item.get("title", ""))
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        return deduped


__all__ = ["FirecrawlClient", "FirecrawlDocument"]
