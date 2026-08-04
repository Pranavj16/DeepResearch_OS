"""Workspace management REST API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.research import get_session
from app.application.workspace.service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


class WorkspaceResponse(BaseModel):
    """Workspace details payload."""

    id: UUID
    name: str
    quotas: dict[str, int]


@router.get("/default", response_model=WorkspaceResponse)
async def get_default_workspace(
    user_email: str = "user@research.ai",
    session: AsyncSession = Depends(get_session),
) -> WorkspaceResponse:
    """Retrieve or create default workspace for user context."""

    service = WorkspaceService(session)
    org, proj, ws, env, user = await service.get_or_create_default_tenancy(user_email)
    return WorkspaceResponse(id=ws.id, name=ws.name, quotas=ws.quotas)


__all__ = ["router"]
