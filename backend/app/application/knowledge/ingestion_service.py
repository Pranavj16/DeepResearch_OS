"""Document acquisition, normalization, and structural chunking ingestion service."""

import hashlib
from uuid import UUID

from app.db.models import ArtifactModel, ChunkModel, DocumentVersionModel, SourceModel
from sqlalchemy.ext.asyncio import AsyncSession


class IngestionService:
    """Service managing document ingestion, content hashing, and structural chunking."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def ingest_web_page(
        self, workspace_id: UUID, url: str, title: str, html_text: str, chunk_size: int = 2000
    ) -> tuple[SourceModel, DocumentVersionModel, list[ChunkModel]]:
        """Ingest a web page document into immutable Artifact, Source, and Chunk records."""

        content_hash = hashlib.sha256(html_text.encode("utf-8")).hexdigest()

        artifact = ArtifactModel(
            uri=url,
            content_hash=content_hash,
            media_type="text/html",
            sensitivity="public",
            retention="standard",
        )
        self._session.add(artifact)
        await self._session.flush()

        source = SourceModel(
            workspace_id=workspace_id,
            url=url,
            title=title,
            source_type="web",
        )
        self._session.add(source)
        await self._session.flush()

        doc_version = DocumentVersionModel(
            source_id=source.id,
            artifact_id=artifact.id,
            version_number=1,
            mime_type="text/html",
        )
        self._session.add(doc_version)
        await self._session.flush()

        # Simple structural chunking by character length
        chunks: list[ChunkModel] = []
        words = html_text.split()
        current_chunk: list[str] = []
        current_len = 0
        chunk_idx = 0

        for word in words:
            current_chunk.append(word)
            current_len += len(word) + 1
            if current_len >= chunk_size:
                chunk_str = " ".join(current_chunk)
                c = ChunkModel(
                    document_version_id=doc_version.id,
                    chunk_index=chunk_idx,
                    text_content=chunk_str,
                )
                self._session.add(c)
                chunks.append(c)
                chunk_idx += 1
                current_chunk = []
                current_len = 0

        if current_chunk:
            c = ChunkModel(
                document_version_id=doc_version.id,
                chunk_index=chunk_idx,
                text_content=" ".join(current_chunk),
            )
            self._session.add(c)
            chunks.append(c)

        await self._session.commit()
        return source, doc_version, chunks


__all__ = ["IngestionService"]
