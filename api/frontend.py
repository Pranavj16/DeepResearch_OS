"""Vercel Serverless Function entrypoint for Django WSGI frontend."""

import os
import sys
from pathlib import Path

# Add frontend directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
frontend_dir = root_dir / "frontend"
if str(frontend_dir) not in sys.path:
    sys.path.insert(0, str(frontend_dir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from config.wsgi import application as app  # noqa: E402
