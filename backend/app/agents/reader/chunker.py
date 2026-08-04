"""Deterministic text chunking for the Reader Agent."""

from __future__ import annotations


def chunk_text(text: str, *, max_characters: int) -> list[str]:
    """Split text on word boundaries without exceeding the configured size.

    A single overlong token is preserved as a standalone chunk so content is never
    silently discarded.
    """
    if max_characters < 1:
        message = "max_characters must be greater than zero."
        raise ValueError(message)

    chunks: list[str] = []
    current_words: list[str] = []
    current_length = 0
    for word in text.split():
        separator_length = 1 if current_words else 0
        proposed_length = current_length + separator_length + len(word)
        if current_words and proposed_length > max_characters:
            chunks.append(" ".join(current_words))
            current_words = [word]
            current_length = len(word)
        else:
            current_words.append(word)
            current_length = proposed_length

    if current_words:
        chunks.append(" ".join(current_words))
    return chunks
