from enum import StrEnum
from functools import lru_cache
from typing import Any, Literal, Union

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Application environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    Global application configuration.

    Loads values from the .env file and environment variables.
    Every module in the project should import settings from here.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_prefix="",
    )

    @model_validator(mode="before")
    @classmethod
    def clean_empty_strings(cls, values: Any) -> Any:
        """Strip empty environment variable strings so field defaults are preserved."""
        if isinstance(values, dict):
            cleaned: dict[str, Any] = {}
            for k, v in values.items():
                if isinstance(v, str) and v.strip() == "":
                    continue
                cleaned[k] = v
            return cleaned
        return values

    # ==========================================================
    # Application
    # ==========================================================

    APP_NAME: str = "Research Assistant"

    APP_VERSION: str = "1.0.0"

    APP_DESCRIPTION: str = "Production-grade Multi-Agent Research Assistant"

    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    SECRET_KEY: SecretStr = SecretStr("deep-research-production-secret-key-2026")

    DEBUG: bool = True

    # ==========================================================
    # API
    # ==========================================================

    API_PREFIX: str = "/api/v1"

    API_TITLE: str = "Research Assistant API"

    API_VERSION: str = APP_VERSION

    # ==========================================================
    # Logging
    # ==========================================================

    LOG_LEVEL: Literal[
        "TRACE",
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    LOG_FORMAT: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level:<8}</level> | "
        "<cyan>{name}</cyan>:"
        "<cyan>{function}</cyan>:"
        "<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    LOG_FILE: str = "logs/app.log"

    LOG_ROTATION: str = "10 MB"

    LOG_RETENTION: str = "10 days"

    LOG_SERIALIZE: bool = False

    # ==========================================================
    # LLM Providers
    # ==========================================================

    NVIDIA_API_KEY: SecretStr = SecretStr("")

    GEMINI_API_KEY: SecretStr = SecretStr("")

    GROQ_API_KEY: SecretStr = SecretStr("")

    OPENROUTER_API_KEY: SecretStr = SecretStr("")

    # ==========================================================
    # Default LLM Configuration
    # ==========================================================

    DEFAULT_PROVIDER: str = "nvidia"

    DEFAULT_MODEL: str = "z-ai/glm-5.2"

    REQUEST_TIMEOUT: int = 60

    MAX_RETRIES: int = 3

    # ==========================================================
    # Tool and Reader Defaults
    # ==========================================================

    TAVILY_API_URL: str = "https://api.tavily.com/search"

    TAVILY_SEARCH_DEPTH: Literal["basic", "advanced"] = "basic"

    TAVILY_TIMEOUT_SECONDS: int = 30

    TAVILY_MAX_RESULTS: int = 5

    READER_TIMEOUT_SECONDS: int = 30

    READER_CHUNK_SIZE: int = 4_000

    # ==========================================================
    # Search
    # ==========================================================

    TAVILY_API_KEY: SecretStr = SecretStr("")

    SERPER_API_KEY: SecretStr = SecretStr("")

    BING_API_KEY: SecretStr = SecretStr("")

    PERPLEXITY_API_KEY: SecretStr = SecretStr("")

    # ==========================================================
    # Database
    # ==========================================================

    DATABASE_URL: str = ""

    # ==========================================================
    # Redis
    # ==========================================================

    REDIS_URL: str = ""

    # ==========================================================
    # Qdrant
    # ==========================================================

    QDRANT_URL: str = ""

    QDRANT_API_KEY: SecretStr = SecretStr("")

    # ==========================================================
    # CORS
    # ==========================================================

    ALLOWED_ORIGINS: Any = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "*",
        ]
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS allowed origins from JSON, comma-separated string, or list."""
        if v is None or v == "":
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                "*",
            ]
        if isinstance(v, str):
            v_clean = v.strip()
            if not v_clean:
                return ["*"]
            if v_clean.startswith("[") and v_clean.endswith("]"):
                try:
                    import json

                    parsed = json.loads(v_clean)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass
            return [i.strip() for i in v_clean.split(",") if i.strip()]
        if isinstance(v, list):
            return [str(i).strip() for i in v if str(i).strip()]
        return ["*"]

    @property
    def tavily_api_key(self) -> str | None:
        """Return the Tavily key without exposing it in logs or repr output."""

        value = self.TAVILY_API_KEY.get_secret_value()
        return value or None

    @property
    def serper_api_key(self) -> str | None:
        """Return the Serper key without exposing it in logs or repr output."""

        value = self.SERPER_API_KEY.get_secret_value()
        return value or None

    @property
    def tavily_api_url(self) -> str:
        """Return the configured Tavily endpoint."""

        return self.TAVILY_API_URL

    @property
    def tavily_search_depth(self) -> str:
        """Return the configured Tavily search depth."""

        return self.TAVILY_SEARCH_DEPTH

    @property
    def tavily_timeout_seconds(self) -> int:
        """Return the Tavily request timeout."""

        return self.TAVILY_TIMEOUT_SECONDS

    @property
    def tavily_max_results(self) -> int:
        """Return the maximum number of search results."""

        return self.TAVILY_MAX_RESULTS

    @property
    def reader_timeout_seconds(self) -> int:
        """Return the reader HTTP timeout."""

        return self.READER_TIMEOUT_SECONDS

    @property
    def reader_chunk_size(self) -> int:
        """Return the reader chunk size."""

        return self.READER_CHUNK_SIZE


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    The configuration is loaded only once during application startup.
    """

    return Settings()


settings = get_settings()
