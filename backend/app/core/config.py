from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Farm Net"
    app_env: str = "development"
    app_debug: bool = False
    app_version: str = "0.1.0"

    api_v1_prefix: str = "/api/v1"

    database_url: str

    redis_url: str = "redis://redis:6379/0"

    auth_dev_otp_enabled: bool = True
    auth_dev_otp_code: str = "111111"
    otp_expire_minutes: int = 2
    otp_max_attempts: int = 5
    otp_rate_limit_seconds: int = 60

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 30
    super_admin_email: str = "admin@example.com"
    super_admin_phone: str = "09120000000"
    super_admin_password: str = "change-me"

    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    rate_limit_enabled: bool = True
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    log_level: str = "INFO"

    email_enabled: bool = False
    email_provider: str = "smtp"
    email_host: str = ""
    email_port: int = 587
    email_user: str = ""
    email_password: str = ""
    email_from: str = ""
    email_starttls: bool = True
    email_use_ssl: bool = False
    email_timeout_seconds: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
