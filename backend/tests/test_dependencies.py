"""Dependency-composition tests."""

from app.core.container import ApplicationContainer, create_container
from app.core.dependencies import get_container, get_llm_router, get_settings_dependency
from app.core.settings import Settings
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


def test_container_composes_process_dependencies() -> None:
    """Container creation must not construct external provider clients."""

    configured = Settings(
        GEMINI_API_KEY="",
        GROQ_API_KEY="",
        NVIDIA_API_KEY="",
        OPENROUTER_API_KEY="",
    )
    container = create_container(configured)

    assert isinstance(container, ApplicationContainer)
    assert container.settings is configured
    assert container.llm_router.available_providers() == []


def test_fastapi_dependency_accessors_read_application_state() -> None:
    """Request dependencies must resolve from application state, not globals."""

    app = FastAPI()
    app.state.container = create_container(Settings())

    @app.get("/dependencies")
    async def dependencies_endpoint(
        container: ApplicationContainer = Depends(get_container),  # noqa: B008
        settings: Settings = Depends(get_settings_dependency),  # noqa: B008
        router=Depends(get_llm_router),  # noqa: B008
    ) -> dict[str, bool]:
        return {
            "container": isinstance(container, ApplicationContainer),
            "settings": isinstance(settings, Settings),
            "router": router is container.llm_router,
        }

    with TestClient(app) as client:
        response = client.get("/dependencies")

    assert response.status_code == 200
    assert response.json() == {"container": True, "settings": True, "router": True}
