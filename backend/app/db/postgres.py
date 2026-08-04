"""Async PostgreSQL connection and session management abstractions using SQLAlchemy 2.0."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.settings import get_settings


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy domain models."""

    pass


import os
from pathlib import Path

def create_engine_from_url(database_url: str | None = None) -> AsyncEngine:
    """Create an AsyncEngine instance configured for production or test databases."""

    url = database_url or get_settings().DATABASE_URL
    if not url:
        # Default in-memory SQLite for testing if no URL provided
        url = "sqlite+aiosqlite:///:memory:"
    elif url.startswith("postgresql://"):
        # Convert dialect for asyncpg driver if needed
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    connect_args: dict[str, Any] = {}
    if "sqlite" in url:
        connect_args["check_same_thread"] = False
        # Automatically ensure parent directory exists for file-based SQLite databases
        if "///" in url and ":memory:" not in url:
            db_path_str = url.split("///")[-1]
            db_path = Path(db_path_str)
            if db_path.parent and not db_path.parent.exists():
                os.makedirs(db_path.parent, exist_ok=True)

    return create_async_engine(
        url,
        echo=False,
        future=True,
        connect_args=connect_args,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a thread-safe async session factory."""

    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@asynccontextmanager
async def get_db_context(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Context manager for acquiring and closing a database session with transaction management."""

    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


__all__ = [
    "Base",
    "create_engine_from_url",
    "create_session_factory",
    "get_db_context",
]
