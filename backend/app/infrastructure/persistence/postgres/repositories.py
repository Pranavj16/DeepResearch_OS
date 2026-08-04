"""Clean Architecture repository implementations for transactional aggregates."""

from typing import Any
from uuid import UUID

from app.db.models import AuditLogModel, JobModel, OrganizationModel, UserModel, WorkspaceModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    """Repository managing User persistence and queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        """Fetch user by primary key."""

        return await self._session.get(UserModel, user_id)

    async def get_by_email(self, email: str) -> UserModel | None:
        """Fetch user by unique email."""

        stmt = select(UserModel).where(UserModel.email == email)
        return await self._session.scalar(stmt)

    async def save(self, user: UserModel) -> UserModel:
        """Persist or update user record."""

        self._session.add(user)
        await self._session.flush()
        return user


class OrganizationRepository:
    """Repository managing Organization persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, org_id: UUID) -> OrganizationModel | None:
        """Fetch organization by primary key."""

        return await self._session.get(OrganizationModel, org_id)

    async def save(self, org: OrganizationModel) -> OrganizationModel:
        """Persist organization record."""

        self._session.add(org)
        await self._session.flush()
        return org


class WorkspaceRepository:
    """Repository managing Workspace persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, workspace_id: UUID) -> WorkspaceModel | None:
        """Fetch workspace by primary key."""

        return await self._session.get(WorkspaceModel, workspace_id)

    async def save(self, workspace: WorkspaceModel) -> WorkspaceModel:
        """Persist workspace record."""

        self._session.add(workspace)
        await self._session.flush()
        return workspace


class AuditLogRepository:
    """Repository logging security and administrative events."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def log_action(
        self,
        action: str,
        resource_type: str,
        user_id: UUID | None = None,
        workspace_id: UUID | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditLogModel:
        """Record an audit log entry."""

        entry = AuditLogModel(
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            workspace_id=workspace_id,
            details=details or {},
        )
        self._session.add(entry)
        await self._session.flush()
        return entry


class JobRepository:
    """Repository managing background worker jobs."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, job_id: UUID) -> JobModel | None:
        """Fetch job record by primary key."""

        return await self._session.get(JobModel, job_id)

    async def enqueue(self, workspace_id: UUID, job_type: str, payload: dict[str, Any]) -> JobModel:
        """Enqueue new background job."""

        job = JobModel(
            workspace_id=workspace_id,
            job_type=job_type,
            status="queued",
            payload=payload,
        )
        self._session.add(job)
        await self._session.flush()
        return job


__all__ = [
    "AuditLogRepository",
    "JobRepository",
    "OrganizationRepository",
    "UserRepository",
    "WorkspaceRepository",
]
