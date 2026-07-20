import time
from collections import OrderedDict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.core.responses import error_response


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int, max_keys: int = 10000) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._requests: OrderedDict[str, deque[float]] = OrderedDict()

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        window_start = now - self.window_seconds
        hits = self._requests.get(key)
        if hits is None:
            if len(self._requests) >= self.max_keys:
                self._requests.popitem(last=False)
            hits = deque()
            self._requests[key] = hits
        else:
            self._requests.move_to_end(key)

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
    search_max_requests: int = 30,
    search_window_seconds: int = 60,
    max_keys: int = 10000,
    trusted_proxy_hosts: set[str] | None = None,
) -> Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]:
    limiter = InMemoryRateLimiter(max_requests, window_seconds, max_keys)
    search_limiter = InMemoryRateLimiter(
        search_max_requests, search_window_seconds, max_keys
    )
    trusted_proxies = trusted_proxy_hosts or set()

    def client_key(request: Request) -> str:
        client_host = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for and client_host in trusted_proxies:
            return forwarded_for.split(",")[0].strip()
        return client_host

    def limited_response(request: Request, retry_after: int) -> JSONResponse:
        trace_id = getattr(request.state, "trace_id", "")
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(retry_after)},
            content=error_response(
                code="RATE_LIMITED",
                message="Too many requests",
                meta={"trace_id": trace_id},
            ),
        )

    async def rate_limit_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not enabled or request.url.path in {"/health", "/api/v1/health"}:
            return await call_next(request)

        key = client_key(request)

        if not limiter.is_allowed(key):
            return limited_response(request, window_seconds)

        if request.url.path == "/api/v1/search" and not search_limiter.is_allowed(key):
            return limited_response(request, search_window_seconds)

        return await call_next(request)

    return rate_limit_middleware
