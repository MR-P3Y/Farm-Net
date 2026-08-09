from functools import lru_cache
from ipaddress import ip_network
from pathlib import Path
from pathlib import PurePosixPath, PureWindowsPath
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Farm Net"
    app_env: str = "development"
    app_debug: bool = False
    app_version: str = "0.1.0"

    api_v1_prefix: str = "/api/v1"

    public_base_url: str = "http://localhost:8000"
    admin_base_url: str = "http://localhost:8080"
    media_base_url: str = "http://localhost:8000/media"

    database_url: str = ""
    database_url_file: str = ""

    redis_url: str = "redis://redis:6379/0"
    redis_url_file: str = ""
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str = ""
    qdrant_api_key_file: str = ""
    qdrant_timeout_seconds: int = 10
    media_storage_dir: str = "storage/media"

    ai_provider_enabled: bool = False
    ai_provider: str = "openai"
    openai_api_key: str = ""
    openai_api_key_file: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_timeout_seconds: int = 60

    auth_dev_otp_enabled: bool = True
    auth_dev_otp_code: str = "111111"
    otp_expire_minutes: int = 2
    otp_max_attempts: int = 5
    otp_rate_limit_seconds: int = 60

    jwt_secret_key: str = "change-me"
    jwt_secret_key_file: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 30
    super_admin_email: str = "admin@example.com"
    super_admin_phone: str = "09120000000"
    super_admin_password: str = "change-me"
    super_admin_password_file: str = ""

    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    rate_limit_enabled: bool = True
    rate_limit_backend: str = "memory"
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60
    rate_limit_max_keys: int = 10000
    search_rate_limit_requests: int = 30
    search_rate_limit_window_seconds: int = 60
    auth_rate_limit_requests: int = 10
    auth_rate_limit_window_seconds: int = 60
    trusted_proxy_hosts: str = ""

    geocoding_enabled: bool = True
    geocoding_provider: str = "nominatim"
    geocoding_base_url: str = "https://nominatim.openstreetmap.org"
    geocoding_user_agent: str = "FarmNet/0.28 (+https://farmnet.ir)"
    geocoding_country_codes: str = "ir"
    geocoding_timeout_seconds: int = 8
    geocoding_cache_ttl_seconds: int = 604800
    geocoding_max_results: int = 5
    geocoding_min_interval_ms: int = 1100

    log_level: str = "INFO"

    email_enabled: bool = False
    email_provider: str = "smtp"
    email_host: str = ""
    email_port: int = 587
    email_user: str = ""
    email_password: str = ""
    email_password_file: str = ""
    email_from: str = ""
    email_starttls: bool = True
    email_use_ssl: bool = False
    email_timeout_seconds: int = 15

    sms_enabled: bool = False
    sms_provider: str = ""
    sms_api_url: str = ""
    sms_api_key: str = ""
    sms_api_key_file: str = ""
    sms_sender: str = ""
    sms_timeout_seconds: int = 15

    push_enabled: bool = False
    push_provider: str = ""
    push_api_url: str = ""
    push_api_key: str = ""
    push_api_key_file: str = ""
    push_timeout_seconds: int = 15

    payment_gateway_enabled: bool = False
    payment_gateway: str = "zarinpal"
    payment_merchant_id: str = ""
    payment_merchant_id_file: str = ""
    payment_callback_base_url: str = ""
    payment_zarinpal_sandbox: bool = True
    payment_gateway_timeout_seconds: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def model_post_init(self, _context: object) -> None:
        secret_fields = (
            ("database_url", "database_url_file"),
            ("redis_url", "redis_url_file"),
            ("jwt_secret_key", "jwt_secret_key_file"),
            ("super_admin_password", "super_admin_password_file"),
            ("email_password", "email_password_file"),
            ("sms_api_key", "sms_api_key_file"),
            ("push_api_key", "push_api_key_file"),
            ("payment_merchant_id", "payment_merchant_id_file"),
            ("qdrant_api_key", "qdrant_api_key_file"),
            ("openai_api_key", "openai_api_key_file"),
        )
        for value_field, file_field in secret_fields:
            secret_file = getattr(self, file_field).strip()
            if not secret_file:
                continue
            try:
                path = Path(secret_file)
                if not path.is_file() or path.is_symlink():
                    raise OSError
                value = path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                raise ValueError(f"Secret file unavailable: {file_field.upper()}") from exc
            if not value or len(value) > 65536:
                raise ValueError(f"Secret file invalid: {file_field.upper()}")
            object.__setattr__(self, value_field, value)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def cors_origin_regex(self) -> str | None:
        """Allow Flutter's random localhost Web port only outside live environments."""
        if self.app_env.strip().lower() in {"development", "test"}:
            return r"^https?://(?:localhost|127\.0\.0\.1)(?::\d+)?$"
        return None

    @property
    def trusted_proxy_host_set(self) -> set[str]:
        return {host.strip() for host in self.trusted_proxy_hosts.split(",") if host.strip()}

    def validate_runtime_safety(self) -> None:
        environment = self.app_env.strip().lower()
        if environment not in {"development", "test", "staging", "production"}:
            raise ValueError("Unsafe runtime configuration: APP_ENV_UNSUPPORTED")

        errors = self._enabled_provider_errors()
        if environment in {"staging", "production"}:
            errors.extend(self._production_like_errors(environment=environment))

        if errors:
            raise ValueError("Unsafe runtime configuration: " + ", ".join(sorted(set(errors))))

    def _enabled_provider_errors(self) -> list[str]:
        errors: list[str] = []
        if self.email_enabled:
            if self.email_provider != "smtp":
                errors.append("EMAIL_PROVIDER_UNSUPPORTED")
            if not self.email_host.strip() or not self.email_from.strip():
                errors.append("EMAIL_CONFIGURATION_INCOMPLETE")
            if not (self.email_starttls or self.email_use_ssl):
                errors.append("EMAIL_TRANSPORT_INSECURE")

        if self.sms_enabled:
            if self.sms_provider != "http_json":
                errors.append("SMS_PROVIDER_UNSUPPORTED")
            if not self._is_https_url(self.sms_api_url) or not all(
                value.strip() for value in (self.sms_api_key, self.sms_sender)
            ):
                errors.append("SMS_CONFIGURATION_INCOMPLETE")

        if self.push_enabled:
            if self.push_provider != "http_json":
                errors.append("PUSH_PROVIDER_UNSUPPORTED")
            if not self._is_https_url(self.push_api_url) or not self.push_api_key.strip():
                errors.append("PUSH_CONFIGURATION_INCOMPLETE")

        if self.payment_gateway_enabled:
            if self.payment_gateway != "zarinpal":
                errors.append("PAYMENT_GATEWAY_UNSUPPORTED")
            if len(self.payment_merchant_id.strip()) != 36:
                errors.append("PAYMENT_MERCHANT_INVALID")
            if not self._is_https_url(self.payment_callback_base_url):
                errors.append("PAYMENT_CALLBACK_INSECURE")
        if self.ai_provider_enabled:
            if self.ai_provider != "openai":
                errors.append("AI_PROVIDER_UNSUPPORTED")
            if not self.openai_api_key.strip():
                errors.append("OPENAI_API_KEY_MISSING")
            if not self._is_https_url(self.openai_base_url):
                errors.append("OPENAI_BASE_URL_INSECURE")
            if not 1 <= self.openai_timeout_seconds <= 600:
                errors.append("OPENAI_TIMEOUT_INVALID")
        if self.geocoding_enabled:
            if self.geocoding_provider != "nominatim":
                errors.append("GEOCODING_PROVIDER_UNSUPPORTED")
            if not self._is_https_url(self.geocoding_base_url):
                errors.append("GEOCODING_BASE_URL_INSECURE")
            if len(self.geocoding_user_agent.strip()) < 12:
                errors.append("GEOCODING_USER_AGENT_INVALID")
            if not 1 <= self.geocoding_timeout_seconds <= 30:
                errors.append("GEOCODING_TIMEOUT_INVALID")
            if not 60 <= self.geocoding_cache_ttl_seconds <= 2592000:
                errors.append("GEOCODING_CACHE_TTL_INVALID")
            if not 1 <= self.geocoding_max_results <= 10:
                errors.append("GEOCODING_MAX_RESULTS_INVALID")
            if self.geocoding_min_interval_ms < 1000:
                errors.append("GEOCODING_INTERVAL_TOO_SHORT")
        return errors

    def _production_like_errors(self, *, environment: str) -> list[str]:
        errors: list[str] = []
        if self.app_debug:
            errors.append("APP_DEBUG_ENABLED")
        if self.auth_dev_otp_enabled:
            errors.append("AUTH_DEV_OTP_ENABLED")
        if self.jwt_algorithm != "HS256":
            errors.append("JWT_ALGORITHM_UNSUPPORTED")
        if len(self.jwt_secret_key.strip()) < 32 or self._is_placeholder(self.jwt_secret_key):
            errors.append("JWT_SECRET_WEAK")
        if len(self.super_admin_password) < 12 or self._is_placeholder(self.super_admin_password):
            errors.append("SUPER_ADMIN_PASSWORD_WEAK")
        if (
            self.super_admin_email.strip().lower() == "admin@example.com"
            or self.super_admin_phone.strip() == "09120000000"
        ):
            errors.append("SUPER_ADMIN_IDENTITY_DEFAULT")

        for name, value in (
            ("PUBLIC_BASE_URL", self.public_base_url),
            ("ADMIN_BASE_URL", self.admin_base_url),
            ("MEDIA_BASE_URL", self.media_base_url),
        ):
            if not self._is_https_url(value):
                errors.append(f"{name}_INSECURE")

        origins = self.cors_origin_list
        if (
            not origins
            or "*" in origins
            or any(not self._is_https_url(origin) for origin in origins)
        ):
            errors.append("CORS_ORIGINS_INSECURE")
        if not self.rate_limit_enabled:
            errors.append("RATE_LIMIT_DISABLED")
        if self.rate_limit_backend != "redis":
            errors.append("RATE_LIMIT_BACKEND_NOT_DISTRIBUTED")
        if not self.trusted_proxy_host_set:
            errors.append("TRUSTED_PROXY_HOSTS_EMPTY")
        else:
            for proxy in self.trusted_proxy_host_set:
                try:
                    network = ip_network(proxy, strict=False)
                except ValueError:
                    errors.append("TRUSTED_PROXY_HOSTS_INVALID")
                    break
                if network.prefixlen == 0:
                    errors.append("TRUSTED_PROXY_HOSTS_OVERBROAD")
                    break

        database = urlparse(self.database_url)
        if not database.password or self._is_placeholder(database.password):
            errors.append("DATABASE_CREDENTIALS_WEAK")
        redis = urlparse(self.redis_url)
        if not redis.password or self._is_placeholder(redis.password):
            errors.append("REDIS_AUTH_MISSING")
        if not self.media_storage_path_is_absolute:
            errors.append("MEDIA_STORAGE_PATH_RELATIVE")
        if (
            environment == "production"
            and self.payment_gateway_enabled
            and self.payment_zarinpal_sandbox
        ):
            errors.append("PAYMENT_SANDBOX_ENABLED")
        return errors

    @staticmethod
    def _is_placeholder(value: str) -> bool:
        normalized = value.strip().lower()
        return not normalized or normalized in {
            "change-me",
            "changeme",
            "password",
            "secret",
            "admin",
        }

    @staticmethod
    def _is_https_url(value: str) -> bool:
        parsed = urlparse(value.strip())
        return parsed.scheme == "https" and bool(parsed.netloc)

    @property
    def media_storage_path_is_absolute(self) -> bool:
        value = self.media_storage_dir.strip()
        return PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute()


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_runtime_safety()
    return settings
