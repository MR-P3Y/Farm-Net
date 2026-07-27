from prometheus_client import Counter, Gauge, Histogram


AI_REQUESTS = Counter(
    "farmnet_ai_requests_total",
    "Barzegar requests by kind and terminal/initial status.",
    ("request_kind", "status"),
)
AI_ATTEMPTS = Counter(
    "farmnet_ai_attempts_total",
    "Barzegar execution attempts by provider, model, and result.",
    ("provider", "model", "status"),
)
AI_PROVIDER_LATENCY = Histogram(
    "farmnet_ai_provider_latency_seconds",
    "Barzegar Provider latency.",
    ("provider", "model"),
    buckets=(0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60),
)
AI_ACTIVE_REQUESTS = Gauge(
    "farmnet_ai_active_requests",
    "Current Barzegar queued/running requests observed by lifecycle events.",
)
AI_SAFETY_BLOCKS = Counter(
    "farmnet_ai_safety_blocks_total",
    "Barzegar safety/output validation blocks.",
    ("code",),
)
AI_ABUSE_REJECTIONS = Counter(
    "farmnet_ai_abuse_rejections_total",
    "Barzegar requests rejected by abuse/concurrency controls.",
    ("reason",),
)


def sync_active_requests(db) -> None:
    from sqlalchemy import func, select

    from app.modules.ai.models import AIRequest

    value = db.scalar(
        select(func.count(AIRequest.id)).where(
            AIRequest.status.in_(("queued", "running"))
        )
    )
    AI_ACTIVE_REQUESTS.set(value or 0)
