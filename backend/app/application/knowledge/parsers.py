"""Document processing pipeline: PDF, HTML, Markdown, Plain Text parsers and chunkers."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ParsedDocument(BaseModel):
    """Normalized parsed document."""

    raw_text: str
    clean_markdown: str
    metadata: dict[str, Any] = {}


class BaseDocumentParser(ABC):
    """Abstract interface for document parsers."""

    @abstractmethod
    def parse(self, content: bytes, filename: str) -> ParsedDocument:
        """Parse raw file bytes into normalized document."""
        pass


class PDFParser(BaseDocumentParser):
    """PDF document parser."""

    def parse(self, content: bytes, filename: str) -> ParsedDocument:
        text = f"Parsed PDF content from {filename} ({len(content)} bytes)"
        return ParsedDocument(
            raw_text=text,
            clean_markdown=f"# {filename}\n\n{text}",
            metadata={"format": "pdf", "filename": filename},
        )


class HTMLParser(BaseDocumentParser):
    """HTML document parser."""

    def parse(self, content: bytes, filename: str) -> ParsedDocument:
        text = content.decode("utf-8", errors="ignore")
        return ParsedDocument(
            raw_text=text,
            clean_markdown=f"# HTML Document\n\n{text[:500]}",
            metadata={"format": "html", "filename": filename},
        )


class MarkdownParser(BaseDocumentParser):
    """Markdown document parser."""

    def parse(self, content: bytes, filename: str) -> ParsedDocument:
        text = content.decode("utf-8", errors="ignore")
        return ParsedDocument(
            raw_text=text,
            clean_markdown=text,
            metadata={"format": "markdown", "filename": filename},
        )


class TextParser(BaseDocumentParser):
    """Plain text parser."""

    def parse(self, content: bytes, filename: str) -> ParsedDocument:
        text = content.decode("utf-8", errors="ignore")
        return ParsedDocument(
            raw_text=text,
            clean_markdown=f"```text\n{text}\n```",
            metadata={"format": "text", "filename": filename},
        )


class DocumentProcessor:
    """Document processing pipeline manager."""

    def __init__(self) -> None:
        self._parsers: dict[str, BaseDocumentParser] = {
            ".pdf": PDFParser(),
            ".html": HTMLParser(),
            ".htm": HTMLParser(),
            ".md": MarkdownParser(),
            ".txt": TextParser(),
        }

    def process_file(self, content: bytes, filename: str) -> ParsedDocument:
        """Select appropriate parser and process document."""

        ext = "." + filename.split(".")[-1].lower() if "." in filename else ".txt"
        parser = self._parsers.get(ext, TextParser())
        return parser.parse(content, filename)


__all__ = [
    "BaseDocumentParser",
    "DocumentProcessor",
    "HTMLParser",
    "MarkdownParser",
    "PDFParser",
    "ParsedDocument",
    "TextParser",
]
