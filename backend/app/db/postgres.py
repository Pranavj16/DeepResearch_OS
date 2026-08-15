"""Async PostgreSQL connection and session management abstractions using SQLAlchemy 2.0."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

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


def create_engine_from_url(database_url: str | None = None) -> AsyncEngine:
    """Create an AsyncEngine instance configured for production (Neon/Postgres) or local SQLite."""

    url = database_url or get_settings().DATABASE_URL
    if not url:
        # Default persistent file-based SQLite database for durable local storage
        try:
            db_dir = Path("storage")
            db_dir.mkdir(parents=True, exist_ok=True)
            url = "sqlite+aiosqlite:///storage/db.sqlite3"
        except OSError:
            url = "sqlite+aiosqlite:////tmp/db.sqlite3"

    connect_args: dict[str, Any] = {}
    engine_kwargs: dict[str, Any] = {
        "echo": False,
        "future": True,
    }

    if "sqlite" in url:
        connect_args["check_same_thread"] = False
        # Automatically ensure parent directory exists for file-based SQLite databases
        if "///" in url and ":memory:" not in url:
            db_path_str = url.split("///")[-1]
            db_path = Path(db_path_str)
            if db_path.parent and not db_path.parent.exists():
                try:
                    os.makedirs(db_path.parent, exist_ok=True)
                except OSError:
                    pass
    else:
        # PostgreSQL / Neon configuration
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Parse and sanitize query parameters for asyncpg compatibility
        try:
            parsed = urlsplit(url)
            if parsed.query:
                query_params = dict(parse_qsl(parsed.query))
                cleaned_params: dict[str, str] = {}
                for k, v in query_params.items():
                    k_lower = k.lower()
                    if k_lower == "sslmode":
                        cleaned_params["ssl"] = "require"
                    elif k_lower in ("channel_binding", "gssencmode", "target_session_attrs"):
                        continue
                    else:
                        cleaned_params[k] = v
                new_query = urlencode(cleaned_params)
                url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment))
        except Exception:
            pass

        # Serverless connection resilience for Neon / Cloud Postgres
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_recycle"] = 300

    return create_async_engine(
        url,
        connect_args=connect_args,
        **engine_kwargs,
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
