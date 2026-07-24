from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from app.core.rate_limit import TrustedProxyResolver


def create_security_headers_middleware(
    *,
    environment: str,
    trusted_proxy_hosts: set[str] | None = None,
) -> Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]:
    proxy_resolver = TrustedProxyResolver(trusted_proxy_hosts)
    is_production = environment.strip().lower() == "production"

    def request_is_https(request: Request) -> bool:
        if request.url.scheme == "https":
            return True
        immediate_host = request.client.host if request.client else "unknown"
        if not proxy_resolver.is_trusted(immediate_host):
            return False
        return request.headers.get("X-Forwarded-Proto", "").lower() == "https"

    async def security_headers_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=()",
        )

        if request.url.path.startswith("/api/") or request.url.path == "/health":
            response.headers.setdefault(
                "Content-Security-Policy",
                "default-src 'none'; frame-ancestors 'none'; "
                "base-uri 'none'; form-action 'none'",
            )

        if request.url.path.startswith(
            (
                "/api/v1/auth/",
                "/api/v1/admin/",
                "/api/v1/profile/",
                "/api/v1/notifications/",
                "/api/v1/finance/",
            )
        ):
            response.headers.setdefault("Cache-Control", "no-store")

        if is_production and request_is_https(request):
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )

        return response

    return security_headers_middleware
