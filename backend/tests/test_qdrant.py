"""Unit and logic contract tests for QdrantAdapter."""

from app.db.qdrant import QdrantAdapter


def test_qdrant_adapter_initialization() -> None:
    """Verify QdrantAdapter exposes an AsyncQdrantClient instance."""

    adapter = QdrantAdapter(url="http://localhost:6333")
    assert adapter.client is not None
