from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.api.middleware import CorrelationIdMiddleware, SecurityHeadersMiddleware
from app.api.router import api_router
from app.core.container import create_container
# Re-trigger uvicorn auto-reload for /research/history endpoint
from app.core.logging import setup_logging
from app.core.settings import settings


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Startup and Shutdown Events."""

    setup_logging()
    fastapi_app.state.container = create_container(settings)

    # Ensure database tables exist and schema is up-to-date
    try:
        from sqlalchemy import text
        from app.db.postgres import create_engine_from_url, Base
        import app.db.models  # noqa: F401
        engine = create_engine_from_url(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            try:
                await conn.execute(text("ALTER TABLE research_runs ADD COLUMN details JSON;"))
            except Exception:
                pass
        await engine.dispose()
    except Exception as err:
        logger.warning(f"Database table initialization warning: {err}")

    logger.info("Starting Research Assistant Backend...")

    yield

    logger.info("Shutting down Research Assistant Backend...")
    fastapi_app.state.container = None


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIdMiddleware)

from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.base import ApplicationError


@app.exception_handler(ApplicationError)
async def application_error_handler(request: Request, exc: ApplicationError):
    """Map application domain errors to HTTP responses with appropriate status code."""
    status_code = 401 if exc.status_code in [401, 403] else exc.status_code
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message, "code": exc.code, "details": exc.details},
    )

app.include_router(
    api_router,
    prefix=settings.API_PREFIX,
)


@app.get("/")
async def root():
    """Root Endpoint."""

    return {
        "message": "Research Assistant Backend",
        "version": settings.APP_VERSION,
    }
