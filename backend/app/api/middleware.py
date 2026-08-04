"""Security, headers, and correlation middleware for FastAPI application."""

import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import bind_context, clear_context


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware injecting correlation ID into request context and response headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", uuid4().hex)
        bind_context(correlation_id=correlation_id)

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"

        clear_context()
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware applying production security headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


__all__ = ["CorrelationIdMiddleware", "SecurityHeadersMiddleware"]
