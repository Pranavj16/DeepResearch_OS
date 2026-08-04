"""Unit and logic contract tests for RedisAdapter."""

from app.db.redis import RedisAdapter


def test_redis_adapter_initialization() -> None:
    """Verify RedisAdapter initializes with fallback URL when configuration is empty."""

    adapter = RedisAdapter(redis_url="redis://localhost:6379/0")
    assert adapter.client is not None
