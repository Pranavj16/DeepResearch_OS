"""Composition root for API route modules."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.events import router as events_router
from app.api.v1.health import router as health_router
from app.api.v1.research import router as research_router
from app.api.v1.roles import router as roles_router
from app.api.v1.workspaces import router as workspaces_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(workspaces_router)
api_router.include_router(roles_router)
api_router.include_router(research_router)
api_router.include_router(events_router)

__all__ = ["api_router"]
