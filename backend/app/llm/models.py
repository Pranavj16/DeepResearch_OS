from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class LLMProvider(StrEnum):
    """
    Supported LLM providers.
    """

    NVIDIA = "nvidia"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    GROQ = "groq"


class MessageRole(StrEnum):
    """
    Chat message roles.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """
    Represents a single chat message.
    """

    role: MessageRole

    content: str


class LLMRequest(BaseModel):
    """
    Standard request passed to any LLM provider.
    """

    provider: LLMProvider

    model: str

    messages: list[ChatMessage]

    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
    )

    max_tokens: int = Field(
        default=4096,
        gt=0,
    )

    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    stream: bool = False


class TokenUsage(BaseModel):
    """
    Token usage information.
    """

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0


class LLMResponse(BaseModel):
    """
    Standard response returned by every provider.
    """

    provider: LLMProvider

    model: str

    content: str

    usage: TokenUsage = Field(
        default_factory=TokenUsage,
    )

    raw_response: Any | None = None
