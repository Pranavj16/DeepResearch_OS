"""Exception contract tests."""

from app.exceptions import (
    AuthorizationError,
    DependencyUnavailableError,
    ExternalServiceError,
    NotFoundError,
    ValidationError,
)


def test_application_errors_expose_stable_metadata() -> None:
    """Errors must carry transport-independent codes and retry metadata."""

    error = ExternalServiceError(
        "search",
        "Search provider timed out.",
        retryable=True,
        request_id="request-1",
    )

    assert str(error) == "Search provider timed out."
    assert error.code == "external_service_error"
    assert error.status_code == 502
    assert error.retryable is True
    assert error.details == {"service": "search", "request_id": "request-1"}


def test_common_errors_have_expected_semantics() -> None:
    """Common failures must classify consistently for future API mapping."""

    assert ValidationError("bad input").status_code == 422
    assert NotFoundError("run", "run-1").status_code == 404
    assert AuthorizationError().status_code == 403
    assert DependencyUnavailableError("postgres").retryable is True
