"""Unit tests for WorkspaceService tenancy resolution."""

import pytest
from app.application.workspace.service import WorkspaceService
from app.db.models import OrganizationModel
from app.db.postgres import Base, create_engine_from_url, create_session_factory
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def async_session():
    engine = create_engine_from_url("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = create_session_factory(engine)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_or_create_default_tenancy(async_session: AsyncSession) -> None:
    service = WorkspaceService(async_session)
    org, proj, ws, env, user = await service.get_or_create_default_tenancy("admin@research.ai")

    assert isinstance(org, OrganizationModel)
    assert user.email == "admin@research.ai"
    assert ws.name == "Default Workspace"
    assert env.name == "development"
