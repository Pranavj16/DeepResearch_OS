"""LLM Providers Package."""

from app.llm.providers.gemini import GeminiLLM
from app.llm.providers.groq import GroqLLM
from app.llm.providers.nvidia import NvidiaLLM
from app.llm.providers.openrouter import OpenRouterLLM

GeminiProvider = GeminiLLM
GroqProvider = GroqLLM
NvidiaProvider = NvidiaLLM
OpenRouterProvider = OpenRouterLLM

class ProviderRegistry:
    """Registry for looking up LLM providers."""
    def __init__(self) -> None:
        self._providers = {
            "gemini": GeminiLLM(),
            "groq": GroqLLM(),
            "nvidia": NvidiaLLM(),
            "openrouter": OpenRouterLLM(),
        }

    def get_provider(self, name: str):
        return self._providers.get(name, GeminiLLM())

__all__ = [
    "GeminiLLM",
    "GeminiProvider",
    "GroqLLM",
    "GroqProvider",
    "NvidiaLLM",
    "NvidiaProvider",
    "OpenRouterLLM",
    "OpenRouterProvider",
    "ProviderRegistry",
]
