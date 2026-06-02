"""
security.py
===========
Security layer: API key authentication, security headers middleware,
and rate limiter setup.
"""

import logging
import time
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# API Key authentication
# ---------------------------------------------------------------------------

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(_api_key_header)) -> str:
    """
    FastAPI dependency that validates the X-API-Key header.
    Returns the key on success; raises 401 on failure.
    Logs failed attempts at WARNING level (without revealing the submitted key).
    """
    if not api_key or api_key != settings.API_KEY:
        logger.warning("Rejected request: invalid or missing API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid or missing API key. "
                               "Provide a valid key in the X-API-Key header.",
                }
            },
        )
    return api_key


# ---------------------------------------------------------------------------
# Security Headers Middleware
# ---------------------------------------------------------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security-related HTTP response headers to every response.
    These headers help protect against common web attacks.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)

        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Legacy XSS filter (still helpful for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Tell browsers to only use HTTPS for the next year
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        # Restrict resource loading to same origin only (API — no UI resources needed)
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        # Don't send referrer information outside of origin
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Disable access to sensitive browser APIs (not needed for an API server)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), camera=(), microphone=(), payment=()"
        )
        # Remove server fingerprint header (MutableHeaders doesn't support .pop())
        if "server" in response.headers:
            del response.headers["server"]
        if "Server" in response.headers:
            del response.headers["Server"]

        return response


# ---------------------------------------------------------------------------
# In-memory Rate Limiter Middleware
# ---------------------------------------------------------------------------
# Uses a simple sliding-window counter per (IP, endpoint-type).
# For production scale you'd use Redis, but this works for PythonAnywhere.

class _RateLimitStore:
    """Thread-safe in-memory sliding window rate limit tracker."""

    def __init__(self) -> None:
        # {ip: [(timestamp, count), ...]}
        self._windows: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        timestamps = self._windows[key]
        # Remove expired entries
        self._windows[key] = [t for t in timestamps if t > cutoff]
        if len(self._windows[key]) >= limit:
            return False
        self._windows[key].append(now)
        return True


_store = _RateLimitStore()

# Parse "60/minute" → (60, 60)
def _parse_rate(rate_str: str) -> tuple[int, int]:
    parts = rate_str.split("/")
    limit = int(parts[0])
    unit = parts[1].lower() if len(parts) > 1 else "minute"
    seconds = {"second": 1, "minute": 60, "hour": 3600}.get(unit, 60)
    return limit, seconds


# Endpoints that are considered "live" (hit external services)
_LIVE_ENDPOINTS = {"/api/v1/news", "/api/v1/news/competitors", "/api/v1/stock"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-IP rate limiting middleware.
    - Live endpoints (news, stock): RATE_LIMIT_LIVE
    - All other endpoints: RATE_LIMIT_STATIC
    """

    def __init__(self, app) -> None:
        super().__init__(app)
        self._static_limit, self._static_window = _parse_rate(settings.RATE_LIMIT_STATIC)
        self._live_limit, self._live_window = _parse_rate(settings.RATE_LIMIT_LIVE)

    def _get_client_ip(self, request: Request) -> str:
        # Respect X-Forwarded-For if behind a proxy (PythonAnywhere uses one)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health check
        if request.url.path in ("/api/v1/health", "/", "/docs", "/openapi.json"):
            return await call_next(request)

        ip = self._get_client_ip(request)
        path = request.url.path

        is_live = any(path.startswith(ep) for ep in _LIVE_ENDPOINTS)
        if is_live:
            key = f"live:{ip}"
            allowed = _store.is_allowed(key, self._live_limit, self._live_window)
            retry_after = self._live_window
        else:
            key = f"static:{ip}"
            allowed = _store.is_allowed(key, self._static_limit, self._static_window)
            retry_after = self._static_window

        if not allowed:
            logger.warning("Rate limit exceeded for IP %s on path %s", ip, path)
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please slow down.",
                    }
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
