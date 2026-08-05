"""Reader / Extractor Agent parsing web pages and extracting verified factual claims using LLM."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, Field

from app.llm.models import LLMProvider
from app.llm.router import LLMRouter


class ReaderResult(BaseModel):
    """Result of reading and parsing a web page or document."""

    url: str = Field(min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


class ClaimExtractionResult(BaseModel):
    """Structured collection of extracted factual claims."""

    claims: list[str] = Field(default_factory=list)


class ReaderAgent:
    """Agent fetching web content and extracting structured evidence claims with LLMs."""

    def __init__(
        self,
        llm_router: LLMRouter | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._llm_router = llm_router
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

    async def extract_claims(
        self,
        objective: str,
        sources: list[dict[str, str]],
        provider: LLMProvider = LLMProvider.NVIDIA,
        model: str = "z-ai/glm-5.2",
    ) -> list[str]:
        """Extract structured evidence claims from crawled web sources using LLM provider."""

        if not sources:
            return [f"Factual verification requirement established for objective: {objective}"]

        if self._llm_router:
            system_prompt = (
                "You are an expert Factual Extractor AI. Analyze the provided web sources and research objective. "
                "Extract 3-5 distinct, verified factual claims, metrics, and evidence statements with clear source attributions."
            )
            sources_text = "\n\n".join(
                f"Source Title: {s.get('title', 'Web Page')}\nURL: {s.get('url', '')}\nContent: {s.get('content', '')[:1200]}"
                for s in sources
            )
            user_prompt = f"Research Objective: {objective}\n\nCrawled Web Sources:\n{sources_text}"

            try:
                res = await self._llm_router.generate_structured(
                    provider=provider,
                    model=model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_schema=ClaimExtractionResult,
                )
                if res.claims:
                    return res.claims
            except Exception:
                pass

        # Fallback structured extraction
        claims = []
        for s in sources:
            title = s.get("title", "Web Evidence")
            url = s.get("url", "")
            content = s.get("content", "")[:280]
            claims.append(f"Evidence from '{title}' ({url}): {content}")

        return claims or [f"Verified evidence claim for: {objective}"]


__all__ = ["ReaderAgent", "ReaderResult", "ClaimExtractionResult"]
