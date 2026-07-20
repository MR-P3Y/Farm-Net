from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.rate_limit import InMemoryRateLimiter, create_rate_limit_middleware


def test_rate_limiter_bounds_distinct_client_memory() -> None:
    limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60, max_keys=2)
    assert limiter.is_allowed("one")
    assert limiter.is_allowed("two")
    assert limiter.is_allowed("three")
    assert list(limiter._requests) == ["two", "three"]


def test_search_has_tighter_limit_retry_after_and_untrusted_xff_is_ignored() -> None:
    app = FastAPI()
    app.middleware("http")(
        create_rate_limit_middleware(
            enabled=True,
            max_requests=10,
            window_seconds=60,
            search_max_requests=1,
            search_window_seconds=30,
            trusted_proxy_hosts=set(),
        )
    )

    @app.post("/api/v1/search")
    def search():
        return {"ok": True}

    client = TestClient(app)
    first = client.post("/api/v1/search", headers={"X-Forwarded-For": "1.1.1.1"})
    limited = client.post("/api/v1/search", headers={"X-Forwarded-For": "2.2.2.2"})

    assert first.status_code == 200
    assert limited.status_code == 429
    assert limited.headers["retry-after"] == "30"
    assert limited.json()["error"]["code"] == "RATE_LIMITED"


def test_forwarded_client_is_used_only_for_allow_listed_immediate_proxy() -> None:
    app = FastAPI()
    app.middleware("http")(
        create_rate_limit_middleware(
            enabled=True,
            max_requests=1,
            window_seconds=60,
            trusted_proxy_hosts={"testclient"},
        )
    )

    @app.get("/resource")
    def resource():
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/resource", headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 200
    assert client.get("/resource", headers={"X-Forwarded-For": "2.2.2.2"}).status_code == 200
