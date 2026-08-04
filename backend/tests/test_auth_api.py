"""API integration tests for Registration, Login, Token Refresh, and Workspaces."""

import pytest
from app.api.v1.research import get_session
from app.db.models import Base
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_session():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    import asyncio

    async def init():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init())


def test_auth_registration_and_login_flow() -> None:
    # 1. Register User
    reg_payload = {
        "email": "platform_lead@research.ai",
        "password": "SecurePassword123!",
        "org_name": "Platform Enterprise Org",
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert "refresh_token" in reg_data

    # 2. Login User
    login_payload = {
        "email": "platform_lead@research.ai",
        "password": "SecurePassword123!",
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["role"] == "owner"

    # 3. Refresh Tokens
    refresh_res = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": login_data["refresh_token"]}
    )
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()


def test_roles_and_workspaces_endpoints() -> None:
    roles_res = client.get("/api/v1/roles")
    assert roles_res.status_code == 200
    roles = roles_res.json()
    assert len(roles) >= 4

    ws_res = client.get("/api/v1/workspaces/default?user_email=platform_lead@research.ai")
    assert ws_res.status_code == 200
    assert ws_res.json()["name"] == "Default Workspace"
