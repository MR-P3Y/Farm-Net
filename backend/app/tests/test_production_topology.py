import json
from pathlib import Path
import sys
import time

import pytest

from app.core.config import Settings
from scripts.check_worker_health import main as check_worker_health
from scripts.run_notification_worker import write_heartbeat


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def test_settings_load_sensitive_values_from_regular_secret_files(tmp_path: Path):
    database_url = tmp_path / "database_url"
    redis_url = tmp_path / "redis_url"
    jwt_secret = tmp_path / "jwt_secret"
    database_url.write_text("mysql+pymysql://user:secret@mysql/farmnet", encoding="utf-8")
    redis_url.write_text("redis://:secret@redis:6379/0", encoding="utf-8")
    jwt_secret.write_text("x" * 48, encoding="utf-8")

    runtime = Settings(
        database_url_file=str(database_url),
        redis_url_file=str(redis_url),
        jwt_secret_key_file=str(jwt_secret),
        _env_file=None,
    )

    assert runtime.database_url.startswith("mysql+pymysql://")
    assert runtime.redis_url.startswith("redis://")
    assert runtime.jwt_secret_key == "x" * 48


def test_missing_secret_file_fails_without_exposing_a_secret(tmp_path: Path):
    missing = tmp_path / "missing-secret"

    with pytest.raises(ValueError) as error:
        Settings(database_url_file=str(missing), _env_file=None)

    assert "DATABASE_URL_FILE" in str(error.value)
    assert "mysql+pymysql" not in str(error.value)


def run_healthcheck(monkeypatch, heartbeat: Path, *extra: str) -> int:
    monkeypatch.setattr(
        sys,
        "argv",
        ["check_worker_health.py", str(heartbeat), *extra],
    )
    return check_worker_health()


def test_worker_heartbeat_reports_fresh_success_and_repeated_failure(monkeypatch, tmp_path):
    heartbeat = tmp_path / "heartbeat.json"
    write_heartbeat(heartbeat, consecutive_failures=0)
    assert run_healthcheck(monkeypatch, heartbeat) == 0

    write_heartbeat(heartbeat, consecutive_failures=5)
    assert (
        run_healthcheck(
            monkeypatch,
            heartbeat,
            "--max-consecutive-failures",
            "5",
        )
        == 1
    )


def test_worker_heartbeat_rejects_stale_or_malformed_state(monkeypatch, tmp_path):
    heartbeat = tmp_path / "heartbeat.json"
    heartbeat.write_text(
        json.dumps(
            {
                "updated_at_epoch": time.time() - 120,
                "consecutive_failures": 0,
            }
        ),
        encoding="utf-8",
    )
    assert run_healthcheck(monkeypatch, heartbeat, "--max-age-seconds", "60") == 1

    heartbeat.write_text("not-json", encoding="utf-8")
    assert run_healthcheck(monkeypatch, heartbeat) == 1


def test_container_and_compose_hardening_contracts_are_present():
    dockerfile = (REPOSITORY_ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")
    compose = (REPOSITORY_ROOT / "infra" / "docker-compose.production.yml").read_text(
        encoding="utf-8"
    )

    assert "USER 10001:10001" in dockerfile
    assert "COPY --chown=farmnet:farmnet scripts ./scripts" in dockerfile
    assert "--no-proxy-headers" in dockerfile
    assert "read_only: true" in compose
    assert "no-new-privileges:true" in compose
    assert "condition: service_completed_successfully" in compose
    assert "internal: true" in compose
    assert "DATABASE_URL_FILE: /run/secrets/database_url" in compose
