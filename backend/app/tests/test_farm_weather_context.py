from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy import CheckConstraint

from app.core.exceptions import AppException
from app.main import app
from app.modules.farms.models import FarmPlotWeatherLink
from app.modules.farms.schemas import (
    FarmWeatherAlertOut,
    FarmWeatherContextOut,
    FarmWeatherForecastOut,
    FarmWeatherSnapshotOut,
)
from app.modules.farms.weather_service import FarmWeatherService
from app.modules.weather.models import WeatherLocation
from app.modules.weather.schemas import WeatherLocationOut


def test_private_weather_location_contract_is_database_enforced() -> None:
    checks = {
        item.name
        for item in WeatherLocation.__table__.constraints
        if isinstance(item, CheckConstraint)
    }
    assert "ck_weather_locations_visibility_owner" in checks
    assert WeatherLocation.__table__.c.owner_user_id.foreign_keys


def test_plot_weather_link_is_one_to_one_and_restricted() -> None:
    table = FarmPlotWeatherLink.__table__
    assert table.c.plot_id.unique
    assert table.c.weather_location_id.unique
    assert {fk.ondelete for fk in table.c.plot_id.foreign_keys} == {"RESTRICT"}
    assert {fk.ondelete for fk in table.c.weather_location_id.foreign_keys} == {
        "RESTRICT"
    }


def test_context_contract_does_not_expose_coordinates_or_weather_location_id() -> None:
    forbidden = {"latitude", "longitude", "location_id", "owner_user_id"}
    for schema in (
        FarmWeatherSnapshotOut,
        FarmWeatherForecastOut,
        FarmWeatherAlertOut,
        FarmWeatherContextOut,
    ):
        assert forbidden.isdisjoint(schema.model_fields)


def test_contextual_weather_requires_exact_plot_coordinates() -> None:
    service = FarmWeatherService(Mock())
    service.plot_service._farm_for_update = Mock(
        return_value=SimpleNamespace(status="active")
    )
    service.plot_service._plot = Mock(
        return_value=SimpleNamespace(
            id=4, status="active", latitude=None, longitude=None
        )
    )
    with pytest.raises(AppException) as exc_info:
        service._location(
            user=SimpleNamespace(id=7), farm_id=2, plot_id=4
        )
    assert exc_info.value.code == "FARM_WEATHER_COORDINATES_REQUIRED"


def test_farm_weather_routes_are_owner_private() -> None:
    paths = app.openapi()["paths"]
    root = "/api/v1/farms/{farm_id}/plots/{plot_id}/weather"
    assert root in paths
    assert f"{root}/refresh" in paths
    assert f"{root}/alerts" in paths
    assert not any("/public/farms" in path for path in paths)


def test_public_weather_location_schema_remains_backward_compatible() -> None:
    fields = WeatherLocationOut.model_fields
    assert "owner_user_id" not in fields
    assert "visibility" not in fields
    assert fields["latitude"].is_required()
    assert fields["longitude"].is_required()
