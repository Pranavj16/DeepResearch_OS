"""FastAPI dependency accessors backed by application state."""

from fastapi import Request

from app.core.container import ApplicationContainer, create_container
from app.core.settings import Settings
from app.llm.router import LLMRouter


def get_container(request: Request = None) -> ApplicationContainer:
    """Return the process container composed during application startup or fallback."""

    container = getattr(request.app.state, "container", None) if request and hasattr(request, "app") else None
    if not isinstance(container, ApplicationContainer):
        from app.core.settings import get_settings
        container = create_container(get_settings())
    return container


def get_settings_dependency(request: Request = None) -> Settings:
    """Return typed settings through the application container."""

    return get_container(request).settings


def get_llm_router(request: Request = None) -> LLMRouter:
    """Return the process-scoped LLM router."""

    return get_container(request).llm_router
