from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.weather.enums import WeatherLocationType, WeatherProvider
from app.modules.weather.models import WeatherForecast, WeatherLocation, WeatherSnapshot
from app.modules.weather.providers.base import WeatherProviderClient, WeatherProviderLocation
from app.modules.weather.providers.mock_provider import MockWeatherProviderClient
from app.modules.weather.providers.openweather_provider import OpenWeatherProviderClient
from app.modules.weather.repository import WeatherRepository
from app.modules.weather.schemas import (
    WeatherAlertOut,
    WeatherForecastOut,
    WeatherGpsLocationIn,
    WeatherLocationCreateIn,
    WeatherLocationOut,
    WeatherProviderConfigOut,
    WeatherSnapshotOut,
)


class WeatherService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = WeatherRepository(db)

    def seed_default_provider_configs(self) -> list[WeatherProviderConfigOut]:
        rows = [
            self.repo.upsert_provider_config(
                provider=WeatherProvider.MOCK.value,
                base_url=None,
                api_key_ref=None,
                is_active=True,
                priority=100,
                settings_json={"description": "Local mock weather provider"},
            ),
            self.repo.upsert_provider_config(
                provider=WeatherProvider.OPENWEATHER.value,
                base_url="https://api.openweathermap.org/data/2.5",
                api_key_ref="OPENWEATHER_API_KEY",
                is_active=False,
                priority=200,
                settings_json={"units": "metric"},
            ),
        ]

        self.repo.commit()

        return [WeatherProviderConfigOut.model_validate(row) for row in rows]

    def create_location(
        self,
        *,
        payload: WeatherLocationCreateIn,
    ) -> WeatherLocationOut:
        self._validate_location_type(payload.location_type)
        self._validate_coordinates(payload.latitude, payload.longitude)

        existing = self.repo.find_location_by_coordinates(
            latitude=payload.latitude,
            longitude=payload.longitude,
        )

        if existing is not None:
            return WeatherLocationOut.model_validate(existing)

        row = WeatherLocation(
            country_code=payload.country_code.upper() if payload.country_code else None,
            province_id=payload.province_id,
            city_id=payload.city_id,
            village_id=payload.village_id,
            province_name=payload.province_name,
            city_name=payload.city_name,
            village_name=payload.village_name,
            display_name=payload.display_name,
            location_type=payload.location_type,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone=payload.timezone,
            is_active=True,
        )

        self.repo.add_location(row)
        self.repo.commit()
        self.repo.refresh(row)

        return WeatherLocationOut.model_validate(row)

    def create_gps_location(
        self,
        *,
        payload: WeatherGpsLocationIn,
    ) -> WeatherLocationOut:
        display_name = payload.display_name or (
            f"GPS {payload.latitude}, {payload.longitude}"
        )

        return self.create_location(
            payload=WeatherLocationCreateIn(
                country_code=None,
                display_name=display_name,
                location_type=WeatherLocationType.GPS.value,
                latitude=payload.latitude,
                longitude=payload.longitude,
                timezone=payload.timezone,
            )
        )

    def list_locations(
        self,
        *,
        q: str | None,
        country_code: str | None,
        location_type: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[WeatherLocationOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if location_type is not None:
            self._validate_location_type(location_type)

        rows, total = self.repo.list_locations_paginated(
            q=q,
            country_code=country_code,
            location_type=location_type,
            page=page,
            page_size=page_size,
        )

        return [WeatherLocationOut.model_validate(row) for row in rows], total

    def refresh_location_weather(
        self,
        *,
        location_id: int,
        provider_override: str | None = None,
    ) -> tuple[WeatherSnapshotOut, list[WeatherForecastOut]]:
        location = self.repo.get_location_by_id(location_id=location_id)

        if location is None:
            raise ValidationAuthError(
                message="Weather location not found",
                details={"location_id": location_id},
            )

        provider = self._provider(provider_override=provider_override)

        provider_location = WeatherProviderLocation(
            latitude=location.latitude,
            longitude=location.longitude,
            display_name=location.display_name,
        )

        current = provider.get_current(location=provider_location)
        forecasts = provider.get_forecast(location=provider_location)

        snapshot = WeatherSnapshot(
            location_id=location.id,
            provider=current.provider,
            temperature_c=current.temperature_c,
            feels_like_c=current.feels_like_c,
            humidity_percent=current.humidity_percent,
            wind_speed_mps=current.wind_speed_mps,
            wind_direction_deg=current.wind_direction_deg,
            pressure_hpa=current.pressure_hpa,
            condition_code=current.condition_code,
            condition_text=current.condition_text,
            raw_json=current.raw_json,
            observed_at=current.observed_at,
        )

        self.repo.add_snapshot(snapshot)

        self.repo.delete_forecasts_for_provider(
            location_id=location.id,
            provider=current.provider,
        )

        forecast_rows: list[WeatherForecast] = []

        for item in forecasts:
            forecast = WeatherForecast(
                location_id=location.id,
                provider=item.provider,
                forecast_type=item.forecast_type,
                forecast_time=item.forecast_time,
                temperature_c=item.temperature_c,
                min_temperature_c=item.min_temperature_c,
                max_temperature_c=item.max_temperature_c,
                humidity_percent=item.humidity_percent,
                precipitation_mm=item.precipitation_mm,
                precipitation_probability=item.precipitation_probability,
                wind_speed_mps=item.wind_speed_mps,
                condition_code=item.condition_code,
                condition_text=item.condition_text,
                raw_json=item.raw_json,
            )
            self.repo.add_forecast(forecast)
            forecast_rows.append(forecast)

        self.repo.commit()
        self.repo.refresh(snapshot)

        for row in forecast_rows:
            self.repo.refresh(row)

        return (
            WeatherSnapshotOut.model_validate(snapshot),
            [WeatherForecastOut.model_validate(row) for row in forecast_rows],
        )

    def latest_snapshot(
        self,
        *,
        location_id: int,
    ) -> WeatherSnapshotOut | None:
        row = self.repo.latest_snapshot(location_id=location_id)

        if row is None:
            return None

        return WeatherSnapshotOut.model_validate(row)

    def current_weather(
        self,
        *,
        location_id: int,
    ) -> WeatherSnapshotOut | None:
        location = self.repo.get_location_by_id(location_id=location_id)

        if location is None:
            raise ValidationAuthError(
                message="Weather location not found",
                details={"location_id": location_id},
            )

        return self.latest_snapshot(location_id=location_id)

    def list_forecasts(
        self,
        *,
        location_id: int,
        forecast_type: str | None = None,
    ) -> list[WeatherForecastOut]:
        rows = self.repo.list_forecasts(
            location_id=location_id,
            forecast_type=forecast_type,
        )

        return [WeatherForecastOut.model_validate(row) for row in rows]

    def forecast(
        self,
        *,
        location_id: int,
        forecast_type: str | None,
    ) -> list[WeatherForecastOut]:
        location = self.repo.get_location_by_id(location_id=location_id)

        if location is None:
            raise ValidationAuthError(
                message="Weather location not found",
                details={"location_id": location_id},
            )

        return self.list_forecasts(
            location_id=location_id,
            forecast_type=forecast_type,
        )

    def active_alerts(
        self,
        *,
        location_id: int,
    ) -> list[WeatherAlertOut]:
        location = self.repo.get_location_by_id(location_id=location_id)

        if location is None:
            raise ValidationAuthError(
                message="Weather location not found",
                details={"location_id": location_id},
            )

        rows = self.repo.list_active_alerts(location_id=location_id)

        return [WeatherAlertOut.model_validate(row) for row in rows]

    def _provider(
        self,
        *,
        provider_override: str | None,
    ) -> WeatherProviderClient:
        if provider_override:
            provider_name = provider_override
            config = None
        else:
            config = self.repo.get_active_provider_config()
            provider_name = config.provider if config else WeatherProvider.MOCK.value

        if provider_name == WeatherProvider.MOCK.value:
            return MockWeatherProviderClient()

        if provider_name == WeatherProvider.OPENWEATHER.value:
            base_url = (
                config.base_url
                if config and config.base_url
                else "https://api.openweathermap.org/data/2.5"
            )
            api_key_ref = (
                config.api_key_ref if config and config.api_key_ref else "OPENWEATHER_API_KEY"
            )

            return OpenWeatherProviderClient(
                base_url=base_url,
                api_key_ref=api_key_ref,
            )

        raise ValidationAuthError(
            message="Unsupported weather provider",
            details={"provider": provider_name},
        )

    def _validate_location_type(self, location_type: str) -> None:
        allowed = {item.value for item in WeatherLocationType}

        if location_type not in allowed:
            raise ValidationAuthError(
                message="Invalid weather location type",
                details={"allowed": sorted(allowed)},
            )

    def _validate_coordinates(
        self,
        latitude: Decimal,
        longitude: Decimal,
    ) -> None:
        if latitude < Decimal("-90") or latitude > Decimal("90"):
            raise ValidationAuthError(
                message="Invalid latitude",
                details={"latitude": str(latitude)},
            )

        if longitude < Decimal("-180") or longitude > Decimal("180"):
            raise ValidationAuthError(
                message="Invalid longitude",
                details={"longitude": str(longitude)},
            )
