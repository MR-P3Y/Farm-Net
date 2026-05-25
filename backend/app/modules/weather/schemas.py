from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class WeatherLocationCreateIn(BaseModel):
    country_code: str | None = Field(default=None, max_length=2)

    province_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None

    province_name: str | None = Field(default=None, max_length=120)
    city_name: str | None = Field(default=None, max_length=120)
    village_name: str | None = Field(default=None, max_length=120)

    display_name: str = Field(min_length=1, max_length=255)
    location_type: str = Field(min_length=2, max_length=30)

    latitude: Decimal
    longitude: Decimal

    timezone: str | None = Field(default=None, max_length=80)


class WeatherLocationOut(BaseModel):
    id: int

    country_code: str | None = None

    province_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None

    province_name: str | None = None
    city_name: str | None = None
    village_name: str | None = None

    display_name: str
    location_type: str

    latitude: Decimal
    longitude: Decimal

    timezone: str | None = None
    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WeatherProviderConfigCreateIn(BaseModel):
    provider: str = Field(min_length=2, max_length=50)
    base_url: str | None = Field(default=None, max_length=500)
    api_key_ref: str | None = Field(default=None, max_length=120)

    is_active: bool = False
    priority: int = 100

    settings_json: dict[str, Any] | None = None


class WeatherProviderConfigOut(BaseModel):
    id: int

    provider: str
    base_url: str | None = None
    api_key_ref: str | None = None

    is_active: bool
    priority: int

    settings_json: dict[str, Any] | None = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WeatherSnapshotOut(BaseModel):
    id: int
    location_id: int
    provider: str

    temperature_c: Decimal | None = None
    feels_like_c: Decimal | None = None
    humidity_percent: Decimal | None = None

    wind_speed_mps: Decimal | None = None
    wind_direction_deg: int | None = None

    pressure_hpa: Decimal | None = None

    condition_code: str | None = None
    condition_text: str | None = None

    observed_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class WeatherForecastOut(BaseModel):
    id: int
    location_id: int
    provider: str
    forecast_type: str

    forecast_time: datetime

    temperature_c: Decimal | None = None
    min_temperature_c: Decimal | None = None
    max_temperature_c: Decimal | None = None

    humidity_percent: Decimal | None = None
    precipitation_mm: Decimal | None = None
    precipitation_probability: Decimal | None = None
    wind_speed_mps: Decimal | None = None

    condition_code: str | None = None
    condition_text: str | None = None

    created_at: datetime

    model_config = {"from_attributes": True}
