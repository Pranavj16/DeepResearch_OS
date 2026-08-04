"""Unit tests for AuthService security and JWT management."""

import pytest
from app.domain.auth.service import AuthService
from app.exceptions.base import AuthorizationError


def test_jwt_create_and_decode() -> None:
    """Verify signing and decoding JWT access tokens."""

    auth = AuthService(secret_key="test-secret-key-12345")
    token = auth.create_access_token(
        subject_id="user_123",
        payload={"role": "admin", "org_id": "org_456"},
    )
    assert isinstance(token, str)

    decoded = auth.decode_access_token(token)
    assert decoded["sub"] == "user_123"
    assert decoded["role"] == "admin"
    assert decoded["org_id"] == "org_456"


def test_invalid_jwt_raises_security_error() -> None:
    """Verify invalid token signature raises AuthorizationError."""

    auth = AuthService(secret_key="test-secret-key-12345")
    with pytest.raises(AuthorizationError):
        auth.decode_access_token("invalid.token.str")
