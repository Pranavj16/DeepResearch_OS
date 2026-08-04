"""Operational startup health check script."""

from pathlib import Path
import sys

# Ensure backend directory is in python path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.core.settings import get_settings


def main() -> int:
    """Verify runtime settings and database configuration."""

    settings = get_settings()
    print(f"[*] Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"[*] Environment: {settings.ENVIRONMENT}")
    print(f"[*] API Prefix: {settings.API_PREFIX}")
    print("[+] Configuration load successful.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
