from app.llm.base import BaseLLM
from app.llm.models import LLMProvider
from app.llm.providers.gemini import GeminiLLM
from app.llm.providers.groq import GroqLLM
from app.llm.providers.nvidia import NvidiaLLM
from app.llm.providers.openrouter import OpenRouterLLM


class LLMFactory:
    _providers = {
        LLMProvider.GEMINI: GeminiLLM,
        LLMProvider.NVIDIA: NvidiaLLM,
        LLMProvider.GROQ: GroqLLM,
        LLMProvider.OPENROUTER: OpenRouterLLM,
    }

    @classmethod
    def create(cls, provider: LLMProvider) -> BaseLLM:

        provider_class = cls._providers.get(provider)

        if provider_class is None:
            raise ValueError(f"Unsupported provider: {provider}")

        return provider_class()
