"""Embedding provider abstraction, batch generation, and vector similarity utilities."""

import math
from abc import ABC, abstractmethod


class BaseEmbeddingProvider(ABC):
    """Abstract embedding model provider interface."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Vector dimension size."""
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Generate embedding vector for search query."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for batch of text chunks."""
        pass


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """Deterministically generated vector embedding provider for testing and dev."""

    def __init__(self, dim: int = 1536) -> None:
        self._dim = dim

    @property
    def dimension(self) -> int:
        return self._dim

    def _generate_vector(self, text: str) -> list[float]:
        val = sum(ord(c) for c in text) % 100 / 100.0
        vec = [(val + i / self._dim) % 1.0 for i in range(self._dim)]
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    async def embed_query(self, text: str) -> list[float]:
        return self._generate_vector(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self._generate_vector(t) for t in texts]


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity score between two embedding vectors."""

    if len(vec_a) != len(vec_b) or not vec_a:
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


__all__ = ["BaseEmbeddingProvider", "MockEmbeddingProvider", "cosine_similarity"]
