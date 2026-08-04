"""Pydantic contracts owned by the Search Agent."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.planner import PlannerResponse


class SearchRequest(BaseModel):
    """Input for a web search derived from a completed research plan."""

    plan: PlannerResponse


class SearchResult(BaseModel):
    """An unmodified search result returned by Tavily.

    ``content`` contains Tavily's returned result content; the application does
    not summarize, interpret, or otherwise transform webpage material.
    """

    title: str = Field(min_length=1)
    url: HttpUrl
    content: str = ""
    score: float | None = None
    published_date: str | None = None


class SearchResponse(BaseModel):
    """Structured Tavily results associated with the planner objective."""

    query: str = Field(min_length=1)
    plan_objective: str = Field(min_length=1)
    results: list[SearchResult]
