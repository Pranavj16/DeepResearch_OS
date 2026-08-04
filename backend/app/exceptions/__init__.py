"""Public application exception types."""

from app.exceptions.base import (
    ApplicationError,
    AuthorizationError,
    ConfigurationError,
    DependencyUnavailableError,
    ExternalServiceError,
    NotFoundError,
    ValidationError,
)

__all__ = [
    "ApplicationError",
    "AuthorizationError",
    "ConfigurationError",
    "DependencyUnavailableError",
    "ExternalServiceError",
    "NotFoundError",
    "ValidationError",
]
