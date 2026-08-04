"""Logging contract tests."""

from pathlib import Path

from app.core.logging import get_logger, setup_logging
from app.core.settings import Settings


def test_logging_creates_configured_file_sink(tmp_path: Path) -> None:
    """Logging setup must create its configured runtime directory."""

    log_file = tmp_path / "runtime" / "app.log"
    setup_logging(
        Settings(
            LOG_FILE=str(log_file),
            LOG_SERIALIZE=True,
        )
    )

    assert log_file.parent.is_dir()


def test_logger_can_bind_execution_context() -> None:
    """Callers must be able to attach traceable execution context."""

    contextual = get_logger(
        correlation_id="corr-1",
        workspace_id="workspace-1",
        run_id="run-1",
    )

    assert contextual is not None
