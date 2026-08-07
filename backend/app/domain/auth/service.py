"""Authentication and JWT token verification domain service."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from app.core.settings import get_settings
from app.exceptions.base import AuthorizationError


class AuthService:
    """Security domain service for JWT access and refresh token management."""

    def __init__(self, secret_key: str | None = None) -> None:
        key = secret_key or get_settings().SECRET_KEY.get_secret_value()
        self._secret_key = key or "default-secret-change-me"
        self._algorithm = "HS256"

    def create_access_token(
        self, subject_id: str, payload: dict[str, Any], expires_delta_minutes: int = 30 * 24 * 60
    ) -> str:
        """Encode a signed JWT access token (default 30 days lifetime)."""

        now = datetime.now(UTC)
        claims = {
            "sub": subject_id,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=expires_delta_minutes),
            **payload,
        }
        return jwt.encode(claims, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, subject_id: str, expires_delta_days: int = 7) -> str:
        """Encode a long-lived signed JWT refresh token."""

        now = datetime.now(UTC)
        claims = {
            "sub": subject_id,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=expires_delta_days),
        }
        return jwt.encode(claims, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decode and validate an incoming JWT token."""

        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError as err:
            raise AuthorizationError("Authentication token has expired.") from err
        except jwt.InvalidTokenError as err:
            raise AuthorizationError("Invalid authentication token signature.") from err


__all__ = ["AuthService"]
