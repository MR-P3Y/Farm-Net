from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WeatherLocation(Base):
    __tablename__ = "weather_locations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"),
        nullable=True, index=True,
    )
    visibility: Mapped[str] = mapped_column(
        String(20), nullable=False, default="public", index=True
    )

    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)

    province_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    city_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    village_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)

    province_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    village_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_type: Mapped[str] = mapped_column(String(30), nullable=False)

    latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)

    timezone: Mapped[str | None] = mapped_column(String(80), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "(visibility = 'public' AND owner_user_id IS NULL) OR "
            "(visibility = 'private' AND owner_user_id IS NOT NULL)",
            name="ck_weather_locations_visibility_owner",
        ),
        Index("ix_weather_locations_lat_lon", "latitude", "longitude"),
        Index("ix_weather_locations_geo_ids", "province_id", "city_id", "village_id"),
    )


class WeatherProviderConfig(Base):
    __tablename__ = "weather_provider_configs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Do not store real API keys here.
    # Store env reference, e.g. OPENWEATHER_API_KEY.
    api_key_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    priority: Mapped[int] = mapped_column(BigInteger, nullable=False, default=100)

    settings_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("provider", name="uq_weather_provider_configs_provider"),
        Index("ix_weather_provider_configs_active_priority", "is_active", "priority"),
    )


class WeatherSnapshot(Base):
    __tablename__ = "weather_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    location_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("weather_locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(String(50), nullable=False)

    temperature_c: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    feels_like_c: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    humidity_percent: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    wind_speed_mps: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    wind_direction_deg: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    pressure_hpa: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)

    condition_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    condition_text: Mapped[str | None] = mapped_column(String(255), nullable=True)

    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    observed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_weather_snapshots_location_observed", "location_id", "observed_at"),
        Index("ix_weather_snapshots_provider_observed", "provider", "observed_at"),
    )


class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    location_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("weather_locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    forecast_type: Mapped[str] = mapped_column(String(30), nullable=False)

    forecast_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

    temperature_c: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    min_temperature_c: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    max_temperature_c: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)

    humidity_percent: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    precipitation_mm: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    precipitation_probability: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    wind_speed_mps: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)

    condition_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    condition_text: Mapped[str | None] = mapped_column(String(255), nullable=True)

    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "location_id",
            "provider",
            "forecast_type",
            "forecast_time",
            name="uq_weather_forecasts_location_provider_type_time",
        ),
        Index("ix_weather_forecasts_location_time", "location_id", "forecast_time"),
        Index("ix_weather_forecasts_provider_time", "provider", "forecast_time"),
    )


class WeatherAlertRule(Base):
    __tablename__ = "weather_alert_rules"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    alert_type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False)

    title_template: Mapped[str] = mapped_column(String(255), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)

    # Example:
    # {"temperature_c_lte": 2}
    # {"wind_speed_mps_gte": 12}
    # {"precipitation_mm_gte": 20}
    rule_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_weather_alert_rules_type_active", "alert_type", "is_active"),
    )


class WeatherAlert(Base):
    __tablename__ = "weather_alerts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    location_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("weather_locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rule_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("weather_alert_rules.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    alert_type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    starts_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_weather_alerts_location_active", "location_id", "is_active"),
        Index("ix_weather_alerts_type_status", "alert_type", "status"),
        Index("ix_weather_alerts_starts_ends", "starts_at", "ends_at"),
    )
