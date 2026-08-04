"""Application use-case service for User Registration, Authentication, and RBAC."""

from uuid import UUID

from app.db.models import OrganizationModel, UserModel
from app.domain.auth.password import PasswordHasher
from app.domain.auth.service import AuthService
from app.exceptions.base import AuthorizationError, ValidationError
from app.infrastructure.persistence.postgres.repositories import (
    AuditLogRepository,
    OrganizationRepository,
    UserRepository,
)
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession


class RegisterUserRequest(BaseModel):
    """Payload for user registration."""

    email: str = Field(min_length=3)
    password: str = Field(min_length=8)
    org_name: str = Field(default="Default Organization")


class LoginUserRequest(BaseModel):
    """Payload for user login."""

    email: str
    password: str


class AuthTokenResponse(BaseModel):
    """Token response payload containing access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: UUID
    role: str


class AuthApplicationService:
    """Application use-case handler for user registration, authentication, and RBAC."""

    ROLE_PERMISSIONS = {
        "owner": {"*"},
        "admin": {"workspace:write", "workspace:read", "research:run", "research:read"},
        "researcher": {"research:run", "research:read"},
        "viewer": {"research:read"},
    }

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._orgs = OrganizationRepository(session)
        self._audit = AuditLogRepository(session)
        self._auth_domain = AuthService()

    async def register(self, req: RegisterUserRequest) -> AuthTokenResponse:
        """Register a new user, password hash, and default tenant org."""

        existing = await self._users.get_by_email(req.email)
        if existing:
            raise ValidationError("User with this email already exists.")

        org = OrganizationModel(name=req.org_name)
        await self._orgs.save(org)

        hashed = PasswordHasher.hash_password(req.password)
        user = UserModel(
            organization_id=org.id,
            email=req.email,
            password_hash=hashed,
            role="owner",
            is_active=True,
            is_verified=True,
        )
        await self._users.save(user)
        await self._audit.log_action("user_registered", "user", user_id=user.id)
        await self._session.commit()

        access_token = self._auth_domain.create_access_token(
            subject_id=str(user.id),
            payload={"role": user.role, "org_id": str(user.organization_id)},
        )
        refresh_token = self._auth_domain.create_refresh_token(subject_id=str(user.id))

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            role=user.role,
        )

    async def login(self, req: LoginUserRequest) -> AuthTokenResponse:
        """Authenticate user credentials and issue tokens."""

        user = await self._users.get_by_email(req.email)
        if not user or not user.password_hash:
            raise AuthorizationError("Invalid email or password.")

        if not PasswordHasher.verify_password(req.password, user.password_hash):
            raise AuthorizationError("Invalid email or password.")

        if not user.is_active:
            raise AuthorizationError("User account is inactive.")

        await self._audit.log_action("user_login", "user", user_id=user.id)
        await self._session.commit()

        access_token = self._auth_domain.create_access_token(
            subject_id=str(user.id),
            payload={"role": user.role, "org_id": str(user.organization_id)},
        )
        refresh_token = self._auth_domain.create_refresh_token(subject_id=str(user.id))

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            role=user.role,
        )

    async def refresh_tokens(self, refresh_token: str) -> AuthTokenResponse:
        """Validate refresh token and issue new access & refresh tokens."""

        claims = self._auth_domain.decode_access_token(refresh_token)
        if claims.get("type") != "refresh":
            raise AuthorizationError("Invalid token type for refresh.")

        user_id = UUID(claims["sub"])
        user = await self._users.get_by_id(user_id)
        if not user or not user.is_active:
            raise AuthorizationError("User is not active.")

        new_access = self._auth_domain.create_access_token(
            subject_id=str(user.id),
            payload={"role": user.role, "org_id": str(user.organization_id)},
        )
        new_refresh = self._auth_domain.create_refresh_token(subject_id=str(user.id))

        return AuthTokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            user_id=user.id,
            role=user.role,
        )

    def check_permission(self, role: str, required_permission: str) -> None:
        """Verify role has required RBAC permission."""

        perms = self.ROLE_PERMISSIONS.get(role, set())
        if "*" in perms or required_permission in perms:
            return
        raise AuthorizationError(f"Role '{role}' lacks permission '{required_permission}'.")


__all__ = [
    "AuthApplicationService",
    "AuthTokenResponse",
    "LoginUserRequest",
    "RegisterUserRequest",
]
