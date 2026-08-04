"""Application dependency composition for the backend process."""

from dataclasses import dataclass

from app.core.settings import Settings
from app.llm.router import LLMRouter


@dataclass(slots=True)
class ApplicationContainer:
    """Own process-scoped dependencies shared by application adapters."""

    settings: Settings
    llm_router: LLMRouter


def create_container(settings: Settings) -> ApplicationContainer:
    """Compose dependencies with active provider clients."""

    router = LLMRouter()
    try:
        from app.llm.factory import LLMFactory
        from app.llm.models import LLMProvider

        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.get_secret_value() and settings.GEMINI_API_KEY.get_secret_value() != "your_gemini_api_key_here":
            try:
                router.register(LLMProvider.GEMINI, LLMFactory.create(LLMProvider.GEMINI))
            except Exception:
                pass

        if settings.NVIDIA_API_KEY and settings.NVIDIA_API_KEY.get_secret_value() and settings.NVIDIA_API_KEY.get_secret_value() != "your_nvidia_api_key_here":
            try:
                router.register(LLMProvider.NVIDIA, LLMFactory.create(LLMProvider.NVIDIA))
            except Exception:
                pass

        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.get_secret_value() and settings.GROQ_API_KEY.get_secret_value() != "your_groq_api_key_here":
            try:
                router.register(LLMProvider.GROQ, LLMFactory.create(LLMProvider.GROQ))
            except Exception:
                pass

        if settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY.get_secret_value() and settings.OPENROUTER_API_KEY.get_secret_value() != "your_openrouter_api_key_here":
            try:
                router.register(LLMProvider.OPENROUTER, LLMFactory.create(LLMProvider.OPENROUTER))
            except Exception:
                pass

    except Exception:
        pass

    return ApplicationContainer(settings=settings, llm_router=router)
