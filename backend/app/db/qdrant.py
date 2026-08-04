"""Qdrant async client abstraction for vector store indexing and workspace-scoped retrieval."""

from typing import Any
from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qmodels

from app.core.settings import get_settings


class QdrantAdapter:
    """Async Qdrant client adapter for collection management and similarity search."""

    def __init__(self, url: str | None = None, api_key: str | None = None) -> None:
        client_url = url or get_settings().QDRANT_URL or "http://localhost:6333"
        key = api_key or (
            get_settings().QDRANT_API_KEY.get_secret_value()
            if get_settings().QDRANT_API_KEY
            else None
        )
        self._client = AsyncQdrantClient(url=client_url, api_key=key)

    @property
    def client(self) -> AsyncQdrantClient:
        """Expose the underlying AsyncQdrantClient instance."""

        return self._client

    async def close(self) -> None:
        """Close the Qdrant async client."""

        await self._client.close()

    async def ensure_collection(self, collection_name: str, vector_size: int = 1536) -> None:
        """Bootstrap a Qdrant collection with cosine distance if it does not already exist."""

        collections = await self._client.get_collections()
        existing_names = [c.name for c in collections.collections]
        if collection_name not in existing_names:
            await self._client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size, distance=qmodels.Distance.COSINE
                ),
            )

    async def upsert_vectors(
        self,
        collection_name: str,
        points: list[tuple[UUID, list[float], dict[str, Any]]],
    ) -> None:
        """Upsert points (id, vector, payload metadata) into specified collection."""

        qpoints = [
            qmodels.PointStruct(id=str(point_id), vector=vector, payload=payload)
            for point_id, vector, payload in points
        ]
        await self._client.upsert(collection_name=collection_name, points=qpoints)

    async def search_similar(
        self,
        collection_name: str,
        vector: list[float],
        workspace_id: UUID,
        limit: int = 5,
        score_threshold: float = 0.5,
    ) -> list[qmodels.ScoredPoint]:
        """Execute workspace-filtered similarity search."""

        query_filter = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="workspace_id",
                    match=qmodels.MatchValue(value=str(workspace_id)),
                )
            ]
        )
        response = await self._client.query_points(
            collection_name=collection_name,
            query=vector,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
        )
        return response.points


__all__ = ["QdrantAdapter"]
