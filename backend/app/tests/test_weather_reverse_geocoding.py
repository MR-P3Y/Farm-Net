from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.modules.weather.providers.base import WeatherReverseGeocodeData
from app.modules.weather.providers.openweather_provider import OpenWeatherProviderClient
from app.modules.weather.schemas import WeatherGpsLocationIn
from app.modules.weather.service import WeatherService


class _Response:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self) -> bytes:
        return json.dumps(
            [{
                "name": "Gorgan",
                "local_names": {"fa": "گرگان", "en": "Gorgan"},
                "state": "Golestan Province",
                "country": "IR",
            }]
        ).encode()


def test_openweather_reverse_geocode_prefers_persian_local_name(monkeypatch) -> None:
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")
    monkeypatch.setattr(
        "app.modules.weather.providers.openweather_provider.urlopen",
        lambda *_args, **_kwargs: _Response(),
    )
    result = OpenWeatherProviderClient().reverse_geocode(
        latitude=Decimal("36.84"),
        longitude=Decimal("54.44"),
        language="fa",
    )
    assert result.name == "گرگان"
    assert result.state == "Golestan Province"


def test_gps_creation_updates_nearby_location_with_resolved_city(monkeypatch) -> None:
    now = datetime.now(UTC)
    existing = SimpleNamespace(
        id=7,
        country_code=None,
        province_id=None,
        city_id=None,
        village_id=None,
        province_name=None,
        city_name=None,
        village_name=None,
        display_name="موقعیت فعلی",
        location_type="gps",
        latitude=Decimal("36.84"),
        longitude=Decimal("54.44"),
        timezone="Asia/Tehran",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    repository = MagicMock()
    repository.find_nearby_gps_location.return_value = existing
    provider = MagicMock()
    provider.reverse_geocode.return_value = WeatherReverseGeocodeData(name="گرگان")
    service = WeatherService(MagicMock())
    service.repo = repository
    monkeypatch.setattr(service, "_provider", lambda **_kwargs: provider)

    result = service.create_gps_location(
        payload=WeatherGpsLocationIn(
            latitude=Decimal("36.8404"),
            longitude=Decimal("54.4405"),
            display_name="موقعیت فعلی",
            timezone="Asia/Tehran",
        )
    )

    assert result.id == 7
    assert result.display_name == "موقعیت فعلی — گرگان"
    repository.commit.assert_called_once()
    repository.add_location.assert_not_called()
