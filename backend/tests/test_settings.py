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

    configured = Settings(
        TAVILY_API_KEY=SecretStr("test-key"),
        SERPER_API_KEY=SecretStr("serper-key"),
    )

    assert configured.tavily_api_key == "test-key"
    assert configured.serper_api_key == "serper-key"
    assert configured.tavily_api_url == configured.TAVILY_API_URL
    assert configured.reader_chunk_size == configured.READER_CHUNK_SIZE
def test_cors_origin_parsing(monkeypatch) -> None:
    """ALLOWED_ORIGINS must support empty string, raw strings, lists, and JSON from env."""

    monkeypatch.setenv("ALLOWED_ORIGINS", "")
    assert "*" in Settings().ALLOWED_ORIGINS

    monkeypatch.setenv("ALLOWED_ORIGINS", "https://example.com,https://app.com")
    assert "https://example.com" in Settings().ALLOWED_ORIGINS

    monkeypatch.setenv("ALLOWED_ORIGINS", '["https://app.com"]')
    assert "https://app.com" in Settings().ALLOWED_ORIGINS


def test_empty_environment_strings_fallback_to_defaults(monkeypatch) -> None:
    """Empty strings in ENVIRONMENT, DEBUG, LOG_LEVEL should fallback to defaults."""

    monkeypatch.setenv("ENVIRONMENT", "")
    monkeypatch.setenv("DEBUG", "")
    monkeypatch.setenv("LOG_LEVEL", "")
    monkeypatch.setenv("TAVILY_SEARCH_DEPTH", "")

    settings = Settings()
    assert settings.ENVIRONMENT == Environment.DEVELOPMENT
    assert settings.DEBUG is True
    assert settings.LOG_LEVEL == "INFO"
    assert settings.TAVILY_SEARCH_DEPTH == "basic"


