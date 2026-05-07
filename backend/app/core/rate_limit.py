import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.core.responses import error_response


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        window_start = now - self.window_seconds
        hits = self._requests[key]

        while hits and hits[0] < window_start:
            hits.popleft()

        if len(hits) >= self.max_requests:
            return False

        hits.append(now)
        return True


def create_rate_limit_middleware(
    enabled: bool,
    max_requests: int,
    window_seconds: int,
) -> Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]:
    limiter = InMemoryRateLimiter(max_requests=max_requests, window_seconds=window_seconds)

    async def rate_limit_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not enabled or request.url.path in {"/health", "/api/v1/health"}:
            return await call_next(request)

        client_host = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        key = forwarded_for.split(",")[0].strip() if forwarded_for else client_host

        if not limiter.is_allowed(key):
            trace_id = getattr(request.state, "trace_id", "")
            return JSONResponse(
                status_code=429,
                content=error_response(
                    code="RATE_LIMITED",
                    message="Too many requests",
                    meta={"trace_id": trace_id},
                ),
            )

        return await call_next(request)

    return rate_limit_middleware
