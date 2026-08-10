"""Unit and integration test suite for AI Infrastructure subsystems."""

import pytest
from app.application.knowledge.embeddings import MockEmbeddingProvider, cosine_similarity
from app.application.knowledge.parsers import DocumentProcessor
from app.infrastructure.storage.file_storage import FileStorageService
from app.llm.models import ChatMessage, LLMProvider, LLMRequest, MessageRole
from app.llm.providers import (
    GeminiProvider,
    ProviderRegistry,
)
from app.prompts.registry import PromptRegistry
from app.tools.firecrawl import FirecrawlClient


@pytest.mark.asyncio
async def test_llm_providers_and_registry() -> None:
    registry = ProviderRegistry()
    assert registry.get_provider("gemini").provider_name == "gemini"
    assert registry.get_provider("nvidia").provider_name == "nvidia"
    assert registry.get_provider("groq").provider_name == "groq"
    assert registry.get_provider("openrouter").provider_name == "openrouter"

    gemini = GeminiProvider()
    req = LLMRequest(
        provider=LLMProvider.GEMINI,
        model="gemini-2.5-flash",
        messages=[ChatMessage(role=MessageRole.USER, content="Research AI Platform")],
    )
    res = await gemini.generate(req)
    assert res.content is not None
    assert res.usage.total_tokens > 0


@pytest.mark.asyncio
async def test_prompt_registry_and_rendering() -> None:
    prompts = PromptRegistry()
    template = prompts.get("planner_system")
    sys_p, user_p = template.render(objective="Multi-Agent Systems")
    assert "Lead Research Planner" in sys_p
    assert "Multi-Agent Systems" in user_p


@pytest.mark.asyncio
async def test_document_processor_and_parsers() -> None:
    processor = DocumentProcessor()
    pdf_doc = processor.process_file(b"%PDF-sample", "report.pdf")
    assert pdf_doc.metadata["format"] == "pdf"

    md_doc = processor.process_file(b"# Research Paper", "paper.md")
    assert md_doc.metadata["format"] == "markdown"


@pytest.mark.asyncio
async def test_embeddings_and_similarity() -> None:
    embedder = MockEmbeddingProvider(dim=128)
    vec1 = await embedder.embed_query("AI Systems")
    vec2 = await embedder.embed_query("AI Systems")
    vec3 = await embedder.embed_query("Database Tuning")

    assert len(vec1) == 128
    assert cosine_similarity(vec1, vec2) > 0.99
    assert cosine_similarity(vec1, vec3) < 1.0


@pytest.mark.asyncio
async def test_firecrawl_and_storage() -> None:
    client = FirecrawlClient()
    doc = await client.extract_url("https://arxiv.org/abs/2401.00001")
    assert "arxiv.org" in str(doc.url)

    storage = FileStorageService()
    artifact = await storage.save_artifact("test.md", b"# Report")
    assert artifact.media_type == "text/markdown"
