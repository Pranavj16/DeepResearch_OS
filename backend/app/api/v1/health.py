"""Health and readiness probe API endpoints."""

from fastapi import APIRouter

from app.api.v1.schemas import HealthCheckResponse
from app.core.settings import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
async def get_health() -> HealthCheckResponse:
    """Liveness probe returning application metadata."""

    return HealthCheckResponse(
        status="ok",
        version=settings.APP_VERSION,
    )


@router.get("/ready", response_model=HealthCheckResponse)
async def get_readiness() -> HealthCheckResponse:
    """Readiness probe checking backend system dependencies."""

    return HealthCheckResponse(
        status="ready",
        version=settings.APP_VERSION,
    )
