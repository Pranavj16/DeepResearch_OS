"""File storage service abstraction for research artifacts, reports, and attachments."""

from pathlib import Path
from uuid import UUID, uuid4

from app.models.platform import ArtifactReference
from pydantic import BaseModel


class StoredFile(BaseModel):
    """File storage reference."""

    file_id: UUID
    filename: str
    uri: str
    size_bytes: int


class FileStorageService:
    """Local and cloud storage abstraction for platform artifacts."""

    def __init__(self, storage_dir: str = "./storage") -> None:
        self._root = Path(storage_dir)
        self._root.mkdir(parents=True, exist_ok=True)

    async def save_artifact(
        self, filename: str, content: bytes, media_type: str = "text/markdown"
    ) -> ArtifactReference:
        """Store content bytes and return immutable ArtifactReference."""

        file_id = uuid4()
        dest_path = self._root / f"{file_id}_{filename}"
        dest_path.write_bytes(content)

        import hashlib

        content_hash = hashlib.sha256(content).hexdigest()

        return ArtifactReference(
            artifact_id=file_id,
            uri=f"file://{dest_path.resolve()}",
            content_hash=content_hash,
            media_type=media_type,
            sensitivity="internal",
            retention="standard",
        )


__all__ = ["FileStorageService", "StoredFile"]
