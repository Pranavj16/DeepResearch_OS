"""Foundation smoke tests for the backend application boundary."""

from app.api.router import api_router
from app.core.settings import settings
from app.main import app


def test_application_metadata_is_configured() -> None:
    """The application must expose metadata from the typed settings boundary."""

    assert app.title == settings.API_TITLE
    assert app.version == settings.API_VERSION


def test_api_router_is_composed() -> None:
    """The application composition must include the API router boundary."""

    assert api_router.routes
    assert settings.API_PREFIX == "/api/v1"
