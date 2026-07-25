import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.config import Settings
from app.core.rate_limit import RedisRateLimiter, create_rate_limit_middleware
from app.core.security_headers import create_security_headers_middleware


def test_auth_routes_have_a_separate_tighter_limit():
    app = FastAPI()
    app.middleware("http")(
        create_rate_limit_middleware(
            enabled=True,
            max_requests=10,
            window_seconds=60,
            auth_max_requests=1,
            auth_window_seconds=45,
        )
    )

    @app.post("/api/v1/auth/otp/request")
    def request_otp():
        return {"ok": True}

    client = TestClient(app)
    assert client.post("/api/v1/auth/otp/request").status_code == 200
    limited = client.post("/api/v1/auth/otp/request")

    assert limited.status_code == 429
    assert limited.headers["retry-after"] == "45"
    assert limited.headers["ratelimit-limit"] == "1"
    assert limited.headers["cache-control"] == "no-store"


def test_proxy_chain_uses_rightmost_untrusted_address_not_spoofed_first_value():
    app = FastAPI()
    app.middleware("http")(
        create_rate_limit_middleware(
            enabled=True,
            max_requests=1,
            window_seconds=60,
            trusted_proxy_hosts={"testclient", "10.0.0.2"},
        )
    )

    @app.get("/resource")
    def resource():
        return {"ok": True}

    client = TestClient(app)
    first = client.get(
        "/resource",
        headers={"X-Forwarded-For": "203.0.113.99, 198.51.100.10, 10.0.0.2"},
    )
    same_real_client = client.get(
        "/resource",
        headers={"X-Forwarded-For": "192.0.2.44, 198.51.100.10, 10.0.0.2"},
    )
    different_real_client = client.get(
        "/resource",
        headers={"X-Forwarded-For": "192.0.2.44, 198.51.100.11, 10.0.0.2"},
    )

    assert first.status_code == 200
    assert same_real_client.status_code == 429
    assert different_real_client.status_code == 200


def test_redis_rate_limit_keys_do_not_store_raw_client_identity():
    class FakeRedis:
        def __init__(self):
            self.keys = []

        async def eval(self, _script, _count, key, _window):
            self.keys.append(key)
            return [1, 30]

    limiter = RedisRateLimiter(
        "redis://unused",
        "auth",
        max_requests=5,
        window_seconds=60,
    )
    fake = FakeRedis()
    limiter.client = fake

    assert asyncio.run(limiter.is_allowed("198.51.100.10"))
    assert "198.51.100.10" not in fake.keys[0]
    assert fake.keys[0].startswith("farmnet:rate-limit:auth:")


def test_distributed_rate_limit_fails_closed_when_redis_is_unavailable(monkeypatch):
    async def unavailable(_self, _key):
        raise RedisConnectionError("unavailable")

    monkeypatch.setattr(RedisRateLimiter, "is_allowed", unavailable)
    app = FastAPI()
    app.middleware("http")(
        create_rate_limit_middleware(
            enabled=True,
            backend="redis",
            redis_url="redis://unused",
            max_requests=10,
            window_seconds=60,
        )
    )

    @app.get("/protected")
    def protected():
        return {"ok": True}

    response = TestClient(app).get("/protected")
    assert response.status_code == 503
    assert response.headers["retry-after"] == "1"
    assert response.json()["error"]["code"] == "RATE_LIMIT_UNAVAILABLE"


def test_security_headers_and_trusted_https_hsts_contract():
    app = FastAPI()
    app.middleware("http")(
        create_security_headers_middleware(
            environment="production",
            trusted_proxy_hosts={"testclient"},
        )
    )

    @app.get("/api/v1/auth/me")
    def me():
        return {"ok": True}

    response = TestClient(app).get(
        "/api/v1/auth/me",
        headers={"X-Forwarded-Proto": "https"},
    )

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["cache-control"] == "no-store"
    assert "default-src 'none'" in response.headers["content-security-policy"]
    assert response.headers["strict-transport-security"].startswith("max-age=31536000")


def test_hsts_does_not_trust_forwarded_proto_from_an_untrusted_client():
    app = FastAPI()
    app.middleware("http")(
        create_security_headers_middleware(
            environment="production",
            trusted_proxy_hosts=set(),
        )
    )

    @app.get("/api/v1/public")
    def public():
        return {"ok": True}

    response = TestClient(app).get(
        "/api/v1/public",
        headers={"X-Forwarded-Proto": "https"},
    )

    assert "strict-transport-security" not in response.headers


def test_production_requires_distributed_rate_limit_and_trusted_proxy():
    runtime = Settings(
        app_env="production",
        app_debug=False,
        public_base_url="https://api.farmnet.example",
        admin_base_url="https://admin.farmnet.example",
        media_base_url="https://media.farmnet.example",
        database_url="mysql+pymysql://user:strong-password@mysql/farmnet",
        redis_url="redis://:strong-password@redis:6379/0",
        media_storage_dir="/srv/farmnet/media",
        auth_dev_otp_enabled=False,
        jwt_secret_key="a-production-secret-with-more-than-32-characters",
        super_admin_email="ops@farmnet.example",
        super_admin_phone="09121111111",
        super_admin_password="strong-admin-password",
        cors_origins="https://app.farmnet.example",
        rate_limit_backend="memory",
        trusted_proxy_hosts="",
        _env_file=None,
    )

    try:
        runtime.validate_runtime_safety()
    except ValueError as error:
        message = str(error)
    else:
        raise AssertionError("unsafe production rate-limit settings passed")

    assert "RATE_LIMIT_BACKEND_NOT_DISTRIBUTED" in message
    assert "TRUSTED_PROXY_HOSTS_EMPTY" in message


def test_production_rejects_overbroad_trusted_proxy_network():
    from app.tests.test_runtime_config_safety import secure_production_settings

    runtime = secure_production_settings(trusted_proxy_hosts="0.0.0.0/0")

    try:
        runtime.validate_runtime_safety()
    except ValueError as error:
        message = str(error)
    else:
        raise AssertionError("overbroad trusted proxy network passed")

    assert "TRUSTED_PROXY_HOSTS_OVERBROAD" in message


def test_runtime_cors_allows_known_headers_and_rejects_unknown_headers():
    from app.main import app

    client = TestClient(app)
    allowed = client.options(
        "/api/v1/auth/me",
        headers={
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization,X-Trace-Id",
        },
    )
    rejected = client.options(
        "/api/v1/auth/me",
        headers={
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Unapproved-Header",
        },
    )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:8080"
    assert rejected.status_code == 400
