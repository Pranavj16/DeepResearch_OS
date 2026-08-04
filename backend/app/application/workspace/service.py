"""Workspace and tenancy domain application service."""

from uuid import UUID

from app.db.models import (
    EnvironmentModel,
    OrganizationModel,
    ProjectModel,
    UserModel,
    WorkspaceModel,
)
from app.exceptions.base import NotFoundError, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class WorkspaceService:
    """Application service managing Organization -> Project -> Workspace tenancy and quotas."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create_default_tenancy(
        self, user_email: str
    ) -> tuple[OrganizationModel, ProjectModel, WorkspaceModel, EnvironmentModel, UserModel]:
        """Bootstrap or retrieve a default tenant hierarchy for a user."""

        stmt = (
            select(UserModel)
            .options(selectinload(UserModel.organization))
            .where(UserModel.email == user_email)
        )
        user = await self._session.scalar(stmt)

        if not user:
            org = OrganizationModel(name="Default Organization")
            self._session.add(org)
            await self._session.flush()

            user = UserModel(organization_id=org.id, email=user_email, role="owner")
            self._session.add(user)
            await self._session.flush()
        else:
            org = user.organization

        project_stmt = (
            select(ProjectModel)
            .options(selectinload(ProjectModel.workspaces))
            .where(ProjectModel.organization_id == org.id)
        )
        project = await self._session.scalar(project_stmt)

        if not project:
            project = ProjectModel(organization_id=org.id, name="Default Project")
            self._session.add(project)
            await self._session.flush()

        ws_stmt = select(WorkspaceModel).where(WorkspaceModel.project_id == project.id)
        workspace = await self._session.scalar(ws_stmt)
        if not workspace:
            workspace = WorkspaceModel(
                project_id=project.id,
                name="Default Workspace",
                quotas={"max_concurrent_runs": 5, "max_daily_budget_usd": 100},
            )
            self._session.add(workspace)
            await self._session.flush()

        env_stmt = select(EnvironmentModel).where(EnvironmentModel.workspace_id == workspace.id)
        env = await self._session.scalar(env_stmt)

        if not env:
            env = EnvironmentModel(workspace_id=workspace.id, name="development")
            self._session.add(env)
            await self._session.flush()

        await self._session.commit()
        return org, project, workspace, env, user

    async def validate_workspace_quota(self, workspace_id: UUID) -> None:
        """Validate workspace resource limits before launching executions."""

        workspace = await self._session.get(WorkspaceModel, workspace_id)
        if not workspace:
            raise NotFoundError(
                message=f"Workspace {workspace_id} not found.",
                error_code="WORKSPACE_NOT_FOUND",
            )

        max_runs = workspace.quotas.get("max_concurrent_runs", 10)
        if max_runs <= 0:
            raise ValidationError(
                message="Workspace concurrent run quota exceeded.",
                error_code="QUOTA_EXCEEDED",
            )


__all__ = ["WorkspaceService"]
