import logging
from time import perf_counter

from fastapi import Request
from prometheus_client import Counter, Gauge, Histogram, Info


REQUEST_COUNT = Counter(
    "farmnet_http_requests_total",
    "HTTP requests completed by method, route, and status.",
    ("method", "route", "status"),
)
REQUEST_DURATION = Histogram(
    "farmnet_http_request_duration_seconds",
    "HTTP request duration by method and normalized route.",
    ("method", "route"),
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
REQUESTS_IN_PROGRESS = Gauge(
    "farmnet_http_requests_in_progress",
    "HTTP requests currently executing.",
)
READINESS = Gauge(
    "farmnet_readiness_dependency",
    "Readiness state for a required dependency (1 ready, 0 unavailable).",
    ("dependency",),
)
APP_INFO = Info("farmnet_app", "Farm-Net application build information.")
for required_dependency in ("database", "redis"):
    READINESS.labels(dependency=required_dependency).set(0)

request_logger = logging.getLogger("farmnet.http")


def configure_app_info(*, version: str, environment: str) -> None:
    APP_INFO.info({"version": version, "environment": environment})


def normalized_route(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) and path else "unmatched"


class RequestObservation:
    def __init__(self, request: Request) -> None:
        self.request = request
        self.started_at = perf_counter()
        REQUESTS_IN_PROGRESS.inc()

    def finish(self, *, status_code: int, trace_id: str) -> None:
        duration = perf_counter() - self.started_at
        route = normalized_route(self.request)
        method = self.request.method
        REQUESTS_IN_PROGRESS.dec()
        REQUEST_COUNT.labels(method=method, route=route, status=str(status_code)).inc()
        REQUEST_DURATION.labels(method=method, route=route).observe(duration)
        request_logger.info(
            "request_completed",
            extra={
                "event": "request_completed",
                "trace_id": trace_id,
                "method": method,
                "route": route,
                "status_code": status_code,
                "duration_ms": round(duration * 1000, 3),
            },
        )

    def fail(self, *, trace_id: str) -> None:
        self.finish(status_code=500, trace_id=trace_id)
