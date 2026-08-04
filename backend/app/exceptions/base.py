"""Framework-neutral application exception taxonomy."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(eq=False)
class ApplicationError(Exception):
    """Base error carrying stable machine-readable failure metadata."""

    code: str
    message: str
    status_code: int = 500
    retryable: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize the standard Exception message."""

        super().__init__(self.message)


class ConfigurationError(ApplicationError):
    """Raised when required runtime configuration is invalid or missing."""

    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(
            code="configuration_error",
            message=message,
            status_code=500,
            details=details,
        )


class DependencyUnavailableError(ApplicationError):
    """Raised when a required platform dependency cannot be reached."""

    def __init__(self, dependency: str, message: str | None = None) -> None:
        super().__init__(
            code="dependency_unavailable",
            message=message or f"Dependency '{dependency}' is unavailable.",
            status_code=503,
            retryable=True,
            details={"dependency": dependency},
        )


class ExternalServiceError(ApplicationError):
    """Raised when an external provider returns an unusable response."""

    def __init__(
        self,
        service: str,
        message: str,
        *,
        retryable: bool = False,
        **details: Any,
    ) -> None:
        super().__init__(
            code="external_service_error",
            message=message,
            status_code=502,
            retryable=retryable,
            details={"service": service, **details},
        )


class ValidationError(ApplicationError):
    """Raised when an input violates an application contract."""

    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(
            code="validation_error",
            message=message,
            status_code=422,
            details=details,
        )


class NotFoundError(ApplicationError):
    """Raised when a requested resource is not visible or does not exist."""

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            code="not_found",
            message=f"{resource} '{identifier}' was not found.",
            status_code=404,
            details={"resource": resource, "identifier": identifier},
        )


class AuthorizationError(ApplicationError):
    """Raised when a principal cannot perform an operation."""

    def __init__(self, message: str = "Operation is not authorized.") -> None:
        super().__init__(
            code="authorization_error",
            message=message,
            status_code=403,
        )
