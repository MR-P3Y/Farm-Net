from __future__ import annotations

import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.weather.enums import WeatherForecastType, WeatherProvider
from app.modules.weather.providers.base import (
    WeatherCurrentData,
    WeatherForecastData,
    WeatherProviderClient,
    WeatherProviderLocation,
    WeatherReverseGeocodeData,
)


class OpenWeatherProviderClient(WeatherProviderClient):
    provider_name = WeatherProvider.OPENWEATHER.value

    def __init__(
        self,
        *,
        base_url: str = "https://api.openweathermap.org/data/2.5",
        api_key_ref: str = "OPENWEATHER_API_KEY",
        timeout_seconds: int = 10,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key_ref = api_key_ref
        self.timeout_seconds = timeout_seconds

    def _api_key(self) -> str:
        value = os.getenv(self.api_key_ref)

        if not value:
            raise ValidationAuthError(
                message="OpenWeather API key is not configured",
                details={"api_key_ref": self.api_key_ref},
            )

        return value

    def get_current(
        self,
        *,
        location: WeatherProviderLocation,
    ) -> WeatherCurrentData:
        data = self._get_json(
            "/weather",
            params={
                "lat": str(location.latitude),
                "lon": str(location.longitude),
                "appid": self._api_key(),
                "units": "metric",
            },
            error_message="OpenWeather current weather request failed",
        )

        weather = (data.get("weather") or [{}])[0]
        main = data.get("main") or {}
        wind = data.get("wind") or {}

        observed_at = datetime.utcfromtimestamp(
            int(data.get("dt") or datetime.utcnow().timestamp())
        )

        return WeatherCurrentData(
            provider=self.provider_name,
            temperature_c=self._decimal_or_none(main.get("temp")),
            feels_like_c=self._decimal_or_none(main.get("feels_like")),
            humidity_percent=self._decimal_or_none(main.get("humidity")),
            wind_speed_mps=self._decimal_or_none(wind.get("speed")),
            wind_direction_deg=wind.get("deg"),
            pressure_hpa=self._decimal_or_none(main.get("pressure")),
            condition_code=str(weather.get("id")) if weather.get("id") is not None else None,
            condition_text=weather.get("description"),
            observed_at=observed_at,
            raw_json=data,
        )

    def get_forecast(
        self,
        *,
        location: WeatherProviderLocation,
    ) -> list[WeatherForecastData]:
        data = self._get_json(
            "/forecast",
            params={
                "lat": str(location.latitude),
                "lon": str(location.longitude),
                "appid": self._api_key(),
                "units": "metric",
            },
            error_message="OpenWeather forecast request failed",
        )

        rows: list[WeatherForecastData] = []

        for item in data.get("list") or []:
            main = item.get("main") or {}
            wind = item.get("wind") or {}
            weather = (item.get("weather") or [{}])[0]
            rain = item.get("rain") or {}
            pop = item.get("pop")

            forecast_time = datetime.utcfromtimestamp(
                int(item.get("dt") or datetime.utcnow().timestamp())
            )

            rows.append(
                WeatherForecastData(
                    provider=self.provider_name,
                    forecast_type=WeatherForecastType.HOURLY.value,
                    forecast_time=forecast_time,
                    temperature_c=self._decimal_or_none(main.get("temp")),
                    min_temperature_c=self._decimal_or_none(main.get("temp_min")),
                    max_temperature_c=self._decimal_or_none(main.get("temp_max")),
                    humidity_percent=self._decimal_or_none(main.get("humidity")),
                    precipitation_mm=self._decimal_or_none(rain.get("3h")),
                    precipitation_probability=self._decimal_or_none(pop),
                    wind_speed_mps=self._decimal_or_none(wind.get("speed")),
                    condition_code=(
                        str(weather.get("id")) if weather.get("id") is not None else None
                    ),
                    condition_text=weather.get("description"),
                    raw_json=item,
                )
            )

        return rows

    def geocode(self, *, query: str) -> tuple[Decimal, Decimal]:
        params = urlencode(
            {"q": f"{query},IR", "limit": "1", "appid": self._api_key()}
        )
        request = Request(
            f"https://api.openweathermap.org/geo/1.0/direct?{params}",
            headers={"Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                rows = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError) as error:
            raise ValidationAuthError(
                message="OpenWeather geocoding request failed",
                details={"reason": str(error)},
            ) from error
        if not rows:
            raise ValidationAuthError(message="Selected city coordinates were not found")
        return Decimal(str(rows[0]["lat"])), Decimal(str(rows[0]["lon"]))

    def reverse_geocode(
        self,
        *,
        latitude: Decimal,
        longitude: Decimal,
        language: str = "fa",
    ) -> WeatherReverseGeocodeData:
        params = urlencode(
            {
                "lat": str(latitude),
                "lon": str(longitude),
                "limit": "1",
                "appid": self._api_key(),
            }
        )
        request = Request(
            f"https://api.openweathermap.org/geo/1.0/reverse?{params}",
            headers={"Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                rows = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError) as error:
            raise ValidationAuthError(
                message="OpenWeather reverse geocoding request failed",
                details={"reason": str(error)},
            ) from error
        if not rows:
            raise ValidationAuthError(message="GPS place name was not found")
        row = rows[0]
        local_names = row.get("local_names") or {}
        name = local_names.get(language) or row.get("name")
        if not name:
            raise ValidationAuthError(message="GPS place name was not found")
        return WeatherReverseGeocodeData(
            name=str(name),
            state=str(row["state"]) if row.get("state") else None,
            country=str(row["country"]) if row.get("country") else None,
        )

    def _get_json(
        self,
        path: str,
        *,
        params: dict[str, str],
        error_message: str,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}?{urlencode(params)}"
        request = Request(url, headers={"Accept": "application/json"})

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise ValidationAuthError(
                message=error_message,
                details={"status_code": error.code, "response": body[:500]},
            ) from error
        except URLError as error:
            raise ValidationAuthError(
                message=error_message,
                details={"reason": str(error.reason)},
            ) from error

        return json.loads(body)

    def _decimal_or_none(self, value: object) -> Decimal | None:
        if value is None:
            return None

        return Decimal(str(value))
