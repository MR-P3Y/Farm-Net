import time
from collections import OrderedDict, deque
from collections.abc import Awaitable, Callable
from hashlib import sha256
from inspect import isawaitable
from ipaddress import ip_address, ip_network
from typing import Protocol

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from redis.exceptions import RedisError

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

    def retry_after(self, _key: str) -> int:
        return self.window_seconds


class RateLimiter(Protocol):
    def is_allowed(self, key: str) -> bool | Awaitable[bool]: ...

    def retry_after(self, key: str) -> int | Awaitable[int]: ...


class RedisRateLimiter:
    _script = """
    local current = redis.call('INCR', KEYS[1])
    if current == 1 then
      redis.call('EXPIRE', KEYS[1], ARGV[1])
    end
    local ttl = redis.call('TTL', KEYS[1])
    return {current, ttl}
    """

    def __init__(
        self,
        redis_url: str,
        namespace: str,
        max_requests: int,
        window_seconds: int,
    ) -> None:
        self.client = Redis.from_url(redis_url, decode_responses=True)
        self.namespace = namespace
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._retry_after: OrderedDict[str, int] = OrderedDict()

    async def is_allowed(self, key: str) -> bool:
        safe_key = sha256(key.encode("utf-8")).hexdigest()
        redis_key = f"farmnet:rate-limit:{self.namespace}:{safe_key}"
        current, ttl = await self.client.eval(
            self._script,
            1,
            redis_key,
            self.window_seconds,
        )
        self._retry_after[key] = max(int(ttl), 1)
        self._retry_after.move_to_end(key)
        if len(self._retry_after) > 10000:
            self._retry_after.popitem(last=False)
        return int(current) <= self.max_requests

    def retry_after(self, key: str) -> int:
        return self._retry_after.get(key, self.window_seconds)


class TrustedProxyResolver:
    def __init__(self, trusted_proxy_hosts: set[str] | None = None) -> None:
        self._trusted_hosts = trusted_proxy_hosts or set()
        self._trusted_networks = []
        for value in self._trusted_hosts:
            try:
                self._trusted_networks.append(ip_network(value, strict=False))
            except ValueError:
                continue

    def is_trusted(self, host: str) -> bool:
        if host in self._trusted_hosts:
            return True
        try:
            address = ip_address(host)
        except ValueError:
            return False
        return any(address in network for network in self._trusted_networks)

    def client_host(self, request: Request) -> str:
        immediate_host = request.client.host if request.client else "unknown"
        if not self.is_trusted(immediate_host):
            return immediate_host

        forwarded_for = request.headers.get("X-Forwarded-For")
        if not forwarded_for:
            return immediate_host

        chain = [item.strip() for item in forwarded_for.split(",") if item.strip()]
        for candidate in reversed(chain):
            try:
                ip_address(candidate)
            except ValueError:
                return immediate_host
            if not self.is_trusted(candidate):
                return candidate
        return immediate_host


def _create_limiter(
    *,
    backend: str,
    redis_url: str,
    namespace: str,
    max_requests: int,
    window_seconds: int,
    max_keys: int,
) -> RateLimiter:
    if backend == "redis":
        return RedisRateLimiter(
            redis_url,
            namespace,
            max_requests,
            window_seconds,
        )
    if backend != "memory":
        raise ValueError("Unsupported rate-limit backend")
    return InMemoryRateLimiter(max_requests, window_seconds, max_keys)


def create_rate_limit_middleware(
    enabled: bool,
    max_requests: int,
    window_seconds: int,
    backend: str = "memory",
    redis_url: str = "",
    search_max_requests: int = 30,
    search_window_seconds: int = 60,
    auth_max_requests: int = 10,
    auth_window_seconds: int = 60,
    max_keys: int = 10000,
    trusted_proxy_hosts: set[str] | None = None,
) -> Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]:
    limiter = _create_limiter(
        backend=backend,
        redis_url=redis_url,
        namespace="general",
        max_requests=max_requests,
        window_seconds=window_seconds,
        max_keys=max_keys,
    )
    search_limiter = _create_limiter(
        backend=backend,
        redis_url=redis_url,
        namespace="search",
        max_requests=search_max_requests,
        window_seconds=search_window_seconds,
        max_keys=max_keys,
    )
    auth_limiter = _create_limiter(
        backend=backend,
        redis_url=redis_url,
        namespace="auth",
        max_requests=auth_max_requests,
        window_seconds=auth_window_seconds,
        max_keys=max_keys,
    )
    proxy_resolver = TrustedProxyResolver(trusted_proxy_hosts)
    auth_paths = {
        "/api/v1/auth/login/email",
        "/api/v1/auth/otp/request",
        "/api/v1/auth/otp/verify",
        "/api/v1/auth/refresh",
    }
    search_paths = {
        "/api/v1/search",
        "/api/v1/geo/search",
        "/api/v1/geo/reverse",
    }

    def limited_response(
        request: Request,
        *,
        retry_after: int,
        limit: int,
    ) -> JSONResponse:
        trace_id = getattr(request.state, "trace_id", "")
        return JSONResponse(
            status_code=429,
            headers={
                "Retry-After": str(retry_after),
                "RateLimit-Limit": str(limit),
                "RateLimit-Remaining": "0",
                "Cache-Control": "no-store",
            },
            content=error_response(
                code="RATE_LIMITED",
                message="Too many requests",
                meta={"trace_id": trace_id},
            ),
        )

    def unavailable_response(request: Request) -> JSONResponse:
        trace_id = getattr(request.state, "trace_id", "")
        return JSONResponse(
            status_code=503,
            headers={"Retry-After": "1", "Cache-Control": "no-store"},
            content=error_response(
                code="RATE_LIMIT_UNAVAILABLE",
                message="Request protection is temporarily unavailable",
                meta={"trace_id": trace_id},
            ),
        )

    async def rate_limit_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not enabled or request.url.path in {"/health", "/api/v1/health"}:
            return await call_next(request)

        key = proxy_resolver.client_host(request)

        try:
            allowed = limiter.is_allowed(key)
            if isawaitable(allowed):
                allowed = await allowed
        except RedisError:
            return unavailable_response(request)
        if not allowed:
            retry = limiter.retry_after(key)
            if isawaitable(retry):
                retry = await retry
            return limited_response(
                request,
                retry_after=retry,
                limit=max_requests,
            )

        if request.url.path in search_paths:
            try:
                search_allowed = search_limiter.is_allowed(key)
                if isawaitable(search_allowed):
                    search_allowed = await search_allowed
            except RedisError:
                return unavailable_response(request)
            if not search_allowed:
                retry = search_limiter.retry_after(key)
                if isawaitable(retry):
                    retry = await retry
                return limited_response(
                    request,
                    retry_after=retry,
                    limit=search_max_requests,
                )

        if request.url.path in auth_paths:
            try:
                auth_allowed = auth_limiter.is_allowed(key)
                if isawaitable(auth_allowed):
                    auth_allowed = await auth_allowed
            except RedisError:
                return unavailable_response(request)
            if not auth_allowed:
                retry = auth_limiter.retry_after(key)
                if isawaitable(retry):
                    retry = await retry
                return limited_response(
                    request,
                    retry_after=retry,
                    limit=auth_max_requests,
                )

        return await call_next(request)

    return rate_limit_middleware
