"""Authentication REST API endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.research import get_session
from app.application.auth.service import (
    AuthApplicationService,
    AuthTokenResponse,
    LoginUserRequest,
    RegisterUserRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RefreshTokenRequest(BaseModel):
    """Payload for token refresh."""

    refresh_token: str


@router.post("/register", response_model=AuthTokenResponse)
async def register_user(
    payload: RegisterUserRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthTokenResponse:
    """Register a new user account and tenant organization."""

    service = AuthApplicationService(session)
    return await service.register(payload)


@router.post("/login", response_model=AuthTokenResponse)
async def login_user(
    payload: LoginUserRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthTokenResponse:
    """Authenticate credentials and receive access/refresh tokens."""

    service = AuthApplicationService(session)
    return await service.login(payload)


@router.post("/refresh", response_model=AuthTokenResponse)
async def refresh_tokens(
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthTokenResponse:
    """Refresh access token using long-lived refresh token."""

    service = AuthApplicationService(session)
    return await service.refresh_tokens(payload.refresh_token)


__all__ = ["router"]
