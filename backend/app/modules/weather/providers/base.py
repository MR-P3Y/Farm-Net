from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class WeatherProviderLocation:
    latitude: Decimal
    longitude: Decimal
    display_name: str | None = None


@dataclass(frozen=True)
class WeatherReverseGeocodeData:
    name: str
    state: str | None = None
    country: str | None = None


@dataclass(frozen=True)
class WeatherCurrentData:
    provider: str

    temperature_c: Decimal | None
    feels_like_c: Decimal | None
    humidity_percent: Decimal | None

    wind_speed_mps: Decimal | None
    wind_direction_deg: int | None

    pressure_hpa: Decimal | None

    condition_code: str | None
    condition_text: str | None

    observed_at: datetime
    raw_json: dict[str, Any] | None = None


@dataclass(frozen=True)
class WeatherForecastData:
    provider: str
    forecast_type: str
    forecast_time: datetime

    temperature_c: Decimal | None
    min_temperature_c: Decimal | None
    max_temperature_c: Decimal | None

    humidity_percent: Decimal | None
    precipitation_mm: Decimal | None
    precipitation_probability: Decimal | None
    wind_speed_mps: Decimal | None

    condition_code: str | None
    condition_text: str | None

    raw_json: dict[str, Any] | None = None


class WeatherProviderClient:
    provider_name: str

    def get_current(
        self,
        *,
        location: WeatherProviderLocation,
    ) -> WeatherCurrentData:
        raise NotImplementedError

    def get_forecast(
        self,
        *,
        location: WeatherProviderLocation,
    ) -> list[WeatherForecastData]:
        raise NotImplementedError

    def reverse_geocode(
        self,
        *,
        latitude: Decimal,
        longitude: Decimal,
        language: str = "fa",
    ) -> WeatherReverseGeocodeData:
        raise NotImplementedError
