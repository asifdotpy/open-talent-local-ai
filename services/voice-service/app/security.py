import asyncio
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        for k, v in SECURITY_HEADERS.items():
            response.headers.setdefault(k, v)
        return response


# TODO: Add rate limiting middleware (e.g., sliding window per IP)
# Suggested approach: in-memory token bucket with IP + path key, configurable burst and rate via env; allowlist health/docs.


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests exceeding a configurable size limit."""

    def __init__(self, app, max_bytes: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > self.max_bytes:
            return Response(status_code=413, content="Payload Too Large")
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory token bucket rate limiter.

    Configurable via env:
      - RATE_LIMIT_BURST: max tokens per bucket (default: 10)
      - RATE_LIMIT_RATE: tokens added per second (default: 5)
    Keys: client IP + path. Allowlist skips health/docs endpoints.
    """

    def __init__(self, app, burst: int = 10, rate_per_sec: int = 5, allowlist: tuple[str, ...] | None = None):
        super().__init__(app)
        self.burst = max(1, burst)
        self.rate = max(1, rate_per_sec)
        self.allowlist = allowlist or ()
        self._lock = asyncio.Lock()
        self._buckets = {}

    def _is_allowlisted(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self.allowlist)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if self._is_allowlisted(path):
            return await call_next(request)

        client_ip = request.client.host if request.client else "anonymous"
        key = f"{client_ip}:{path}"
        now = time.monotonic()

        async with self._lock:
            tokens, last = self._buckets.get(key, (self.burst, now))
            # Refill tokens
            elapsed = max(0.0, now - last)
            tokens = min(self.burst, tokens + elapsed * self.rate)
            if tokens < 1:
                return Response(status_code=429, content="Too Many Requests")
            tokens -= 1
            self._buckets[key] = (tokens, now)

        return await call_next(request)
