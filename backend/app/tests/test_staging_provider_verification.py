from app.core.config import Settings
from scripts.verify_staging_providers import CONFIRMATION, safe_code, verify_provider


def settings(**overrides) -> Settings:
    values = {
        "app_env": "development",
        "database_url": "mysql+pymysql://user:strong-password@mysql/farmnet",
        "redis_url": "redis://:strong-password@redis:6379/0",
        "jwt_secret_key": "x" * 48,
        "super_admin_email": "ops@farmnet.test",
        "super_admin_phone": "09121111111",
        "super_admin_password": "strong-admin-password",
        "_env_file": None,
    }
    values.update(overrides)
    return Settings(**values)


def test_disabled_provider_is_never_claimed_ready():
    outcome = verify_provider(
        settings(email_enabled=False),
        "email",
        execute=False,
        confirmation="",
    )

    assert outcome["status"] == "blocked"
    assert outcome["code"] == "PROVIDER_DISABLED"


def test_execute_requires_staging_even_with_explicit_confirmation():
    outcome = verify_provider(
        settings(
            email_enabled=True,
            email_host="smtp.farmnet.test",
            email_from="staging@farmnet.test",
            email_starttls=True,
        ),
        "email",
        execute=True,
        confirmation=CONFIRMATION,
    )

    assert outcome["status"] == "blocked"
    assert outcome["code"] == "STAGING_ENVIRONMENT_REQUIRED"


def test_payment_execute_refuses_non_sandbox_before_network():
    runtime = settings(
        app_env="staging",
        public_base_url="https://api.farmnet.test",
        admin_base_url="https://admin.farmnet.test",
        media_base_url="https://api.farmnet.test/media",
        cors_origins="https://app.farmnet.test",
        rate_limit_backend="redis",
        trusted_proxy_hosts="172.28.0.0/24",
        media_storage_dir="/srv/farmnet/media",
        auth_dev_otp_enabled=False,
        payment_gateway_enabled=True,
        payment_merchant_id="a" * 36,
        payment_callback_base_url="https://api.farmnet.test/callback",
        payment_zarinpal_sandbox=False,
    )

    outcome = verify_provider(
        runtime,
        "payment",
        execute=True,
        confirmation=CONFIRMATION,
    )

    assert outcome["status"] == "blocked"
    assert outcome["code"] == "PAYMENT_SANDBOX_REQUIRED"


def test_external_error_code_is_bounded_and_sanitized():
    assert safe_code("sms_http_429") == "SMS_HTTP_429"
    assert safe_code("secret value from provider") == "PROVIDER_REJECTED"
