"""Pydantic contracts owned by the Reader Agent."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class ReaderRequest(BaseModel):
    """URLs whose readable page content should be retrieved and summarized."""

    urls: list[HttpUrl] = Field(min_length=1)


class ChunkSummary(BaseModel):
    """The source text and structured summary for one readable-content chunk."""

    index: int = Field(ge=1)
    content: str = Field(min_length=1)
    summary: str = Field(min_length=1)


class ReaderPageResult(BaseModel):
    """The processing outcome for one requested URL."""

    url: HttpUrl
    title: str | None = None
    content: str | None = None
    chunks: list[ChunkSummary] = Field(default_factory=list)
    error: str | None = None


class ReaderResponse(BaseModel):
    """Structured results for all URLs supplied to the Reader Agent."""

    pages: list[ReaderPageResult]


class ChunkSummaryResponse(BaseModel):
    """Schema enforced for a single LLM-generated chunk summary."""

    summary: str = Field(min_length=1)
