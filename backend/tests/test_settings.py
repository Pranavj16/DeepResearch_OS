"""Configuration contract tests."""

from app.core.settings import Environment, Settings
from pydantic import SecretStr


def test_settings_have_safe_runtime_defaults() -> None:
    """A settings instance must be usable without provider credentials."""

    configured = Settings()

    assert configured.ENVIRONMENT is Environment.DEVELOPMENT
    assert configured.REQUEST_TIMEOUT > 0
    assert configured.MAX_RETRIES >= 0
    assert configured.TAVILY_MAX_RESULTS > 0
    assert configured.READER_CHUNK_SIZE > 0


def test_legacy_tool_accessors_use_typed_fields() -> None:
    """Existing callers must resolve through the typed configuration fields."""

    configured = Settings(TAVILY_API_KEY=SecretStr("test-key"))

    assert configured.tavily_api_key == "test-key"
    assert configured.tavily_api_url == configured.TAVILY_API_URL
    assert configured.reader_chunk_size == configured.READER_CHUNK_SIZE
