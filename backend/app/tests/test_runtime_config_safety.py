from types import SimpleNamespace

import pytest

from app.core.config import Settings
from app.modules.auth.service import AuthService


def settings(**overrides) -> Settings:
    values = {
        "database_url": "mysql+pymysql://farmnet_user:change-me@mysql/farmnet_db",
        "_env_file": None,
    }
    values.update(overrides)
    return Settings(**values)


def secure_production_settings(**overrides) -> Settings:
    values = {
        "app_env": "production",
        "app_debug": False,
        "public_base_url": "https://api.farmnet.example",
        "admin_base_url": "https://admin.farmnet.example",
        "media_base_url": "https://media.farmnet.example",
        "database_url": ("mysql+pymysql://farmnet_user:strong-database-password@mysql/farmnet_db"),
        "redis_url": "redis://:strong-redis-password@redis:6379/0",
        "media_storage_dir": "/srv/farmnet/media",
        "auth_dev_otp_enabled": False,
        "jwt_secret_key": "a-production-secret-with-more-than-32-characters",
        "super_admin_email": "ops@farmnet.example",
        "super_admin_phone": "09121111111",
        "super_admin_password": "strong-admin-password",
        "cors_origins": ("https://app.farmnet.example,https://admin.farmnet.example"),
        "rate_limit_backend": "redis",
        "trusted_proxy_hosts": "10.10.0.10",
        "_env_file": None,
    }
    values.update(overrides)
    return Settings(**values)


def test_development_defaults_remain_usable() -> None:
    settings().validate_runtime_safety()


def test_production_rejects_unsafe_defaults_without_exposing_values() -> None:
    runtime = settings(app_env="production")

    with pytest.raises(ValueError) as exc_info:
        runtime.validate_runtime_safety()

    message = str(exc_info.value)
    assert "AUTH_DEV_OTP_ENABLED" in message
    assert "JWT_SECRET_WEAK" in message
    assert "DATABASE_CREDENTIALS_WEAK" in message
    assert "REDIS_AUTH_MISSING" in message
    assert "change-me" not in message


def test_secure_production_contract_passes() -> None:
    secure_production_settings().validate_runtime_safety()


def test_enabled_providers_fail_closed_on_incomplete_or_insecure_config() -> None:
    runtime = settings(
        sms_enabled=True,
        sms_provider="http_json",
        sms_api_url="http://sms.invalid/send",
        sms_api_key="",
        sms_sender="",
    )

    with pytest.raises(ValueError, match="SMS_CONFIGURATION_INCOMPLETE"):
        runtime.validate_runtime_safety()


def test_geocoding_rejects_insecure_endpoint_and_policy_interval() -> None:
    runtime = settings(
        geocoding_base_url="http://nominatim.invalid",
        geocoding_min_interval_ms=500,
    )

    with pytest.raises(ValueError) as exc_info:
        runtime.validate_runtime_safety()

    message = str(exc_info.value)
    assert "GEOCODING_BASE_URL_INSECURE" in message
    assert "GEOCODING_INTERVAL_TOO_SHORT" in message


def test_production_rejects_enabled_payment_sandbox() -> None:
    runtime = secure_production_settings(
        payment_gateway_enabled=True,
        payment_merchant_id="m" * 36,
        payment_callback_base_url="https://api.farmnet.example/payment/callback",
        payment_zarinpal_sandbox=True,
    )

    with pytest.raises(ValueError, match="PAYMENT_SANDBOX_ENABLED"):
        runtime.validate_runtime_safety()


def test_disabled_dev_otp_uses_cryptographic_random_source(monkeypatch) -> None:
    service = AuthService.__new__(AuthService)
    service.settings = SimpleNamespace(
        auth_dev_otp_enabled=False,
        auth_dev_otp_code="111111",
    )
    monkeypatch.setattr("app.modules.auth.service.secrets.randbelow", lambda _: 234567)

    assert service._get_dev_otp_code() == "234567"


def test_enabled_dev_otp_preserves_development_code() -> None:
    service = AuthService.__new__(AuthService)
    service.settings = SimpleNamespace(
        auth_dev_otp_enabled=True,
        auth_dev_otp_code="111111",
    )

    assert service._get_dev_otp_code() == "111111"
