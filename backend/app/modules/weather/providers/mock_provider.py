from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from app.modules.weather.enums import WeatherForecastType, WeatherProvider
from app.modules.weather.providers.base import (
    WeatherCurrentData,
    WeatherForecastData,
    WeatherProviderClient,
    WeatherProviderLocation,
)


class MockWeatherProviderClient(WeatherProviderClient):
    provider_name = WeatherProvider.MOCK.value

    def get_current(
        self,
        *,
        location: WeatherProviderLocation,
    ) -> WeatherCurrentData:
        now = datetime.utcnow()

        return WeatherCurrentData(
            provider=self.provider_name,
            temperature_c=Decimal("24.50"),
            feels_like_c=Decimal("25.10"),
            humidity_percent=Decimal("42.00"),
            wind_speed_mps=Decimal("3.20"),
            wind_direction_deg=180,
            pressure_hpa=Decimal("1012.00"),
            condition_code="clear",
            condition_text="Clear sky",
            observed_at=now,
            raw_json={
                "mock": True,
                "display_name": location.display_name,
                "latitude": str(location.latitude),
                "longitude": str(location.longitude),
            },
        )

    def get_forecast(
        self,
        *,
        location: WeatherProviderLocation,
    ) -> list[WeatherForecastData]:
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        rows: list[WeatherForecastData] = []

        for hour in range(1, 25, 3):
            forecast_time = now + timedelta(hours=hour)

            rows.append(
                WeatherForecastData(
                    provider=self.provider_name,
                    forecast_type=WeatherForecastType.HOURLY.value,
                    forecast_time=forecast_time,
                    temperature_c=Decimal(str(22 + (hour % 6))),
                    min_temperature_c=None,
                    max_temperature_c=None,
                    humidity_percent=Decimal("45.00"),
                    precipitation_mm=Decimal("0.00"),
                    precipitation_probability=Decimal("0.00"),
                    wind_speed_mps=Decimal("3.50"),
                    condition_code="clear",
                    condition_text="Clear sky",
                    raw_json={
                        "mock": True,
                        "hour": hour,
                        "display_name": location.display_name,
                    },
                )
            )

        return rows
