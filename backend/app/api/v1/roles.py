"""Roles and permissions RBAC API router."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/roles", tags=["Roles"])


class RoleInfo(BaseModel):
    """RBAC role definition."""

    role: str
    permissions: list[str]


@router.get("", response_model=list[RoleInfo])
async def list_roles() -> list[RoleInfo]:
    """List available RBAC platform roles and permissions."""

    return [
        RoleInfo(role="owner", permissions=["*"]),
        RoleInfo(
            role="admin",
            permissions=["workspace:write", "workspace:read", "research:run", "research:read"],
        ),
        RoleInfo(role="researcher", permissions=["research:run", "research:read"]),
        RoleInfo(role="viewer", permissions=["research:read"]),
    ]


__all__ = ["router"]
