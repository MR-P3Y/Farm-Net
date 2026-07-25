import json
import logging
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.logging import JsonFormatter
from app.main import app
from app.modules.health import observability_router


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def test_liveness_is_dependency_free_and_trace_is_sanitized():
    response = TestClient(app).get(
        "/live",
        headers={"X-Trace-Id": "unsafe\ntrace"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {"app": "ok"}
    assert response.headers["X-Trace-Id"] != "unsafe\ntrace"


def test_readiness_returns_503_when_required_dependency_is_unavailable(monkeypatch):
    monkeypatch.setattr(
        observability_router,
        "get_health_status",
        lambda _db: {"app": "ok", "database": "ok", "redis": "error"},
    )

    response = TestClient(app).get("/ready")

    assert response.status_code == 503
    assert response.json()["data"]["ready"] is False
    assert response.json()["data"]["redis"] == "error"


def test_metrics_are_prometheus_text_and_use_normalized_routes():
    client = TestClient(app)
    assert client.get("/live?token=must-not-be-a-label").status_code == 200

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "farmnet_http_requests_total" in response.text
    assert 'route="/live"' in response.text
    assert "must-not-be-a-label" not in response.text


def test_json_log_formatter_emits_structured_safe_request_fields():
    record = logging.LogRecord(
        name="farmnet.http",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.event = "request_completed"
    record.trace_id = "trace-1"
    record.method = "GET"
    record.route = "/orders/{order_id}"
    record.status_code = 200
    record.duration_ms = 12.5

    payload = json.loads(JsonFormatter().format(record))

    assert payload["event"] == "request_completed"
    assert payload["route"] == "/orders/{order_id}"
    assert "query" not in payload
    assert "body" not in payload


def test_observability_topology_is_internal_and_alert_rules_are_present():
    compose = (REPOSITORY_ROOT / "infra" / "docker-compose.production.yml").read_text(
        encoding="utf-8"
    )
    nginx = (REPOSITORY_ROOT / "infra" / "nginx" / "farmnet.conf").read_text(
        encoding="utf-8"
    )
    alerts = (REPOSITORY_ROOT / "infra" / "observability" / "alerts.yml").read_text(
        encoding="utf-8"
    )

    assert "prom/prometheus:v3.5.0@sha256:" in compose
    assert "prom/alertmanager:v0.28.1@sha256:" in compose
    assert "location = /metrics" in nginx
    assert "location = /ready" in nginx
    assert "FarmNetApiUnavailable" in alerts
    assert "FarmNetHighServerErrorRatio" in alerts
