from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint

from app.core.exceptions import AppException
from app.main import app
from app.modules.farms.models import Farm, FarmPlot
from app.modules.farms.schemas import FarmGeoPoint, FarmPlotCreateIn
from app.modules.farms.service import FarmPlotService


def _farm(area: str = "1000") -> SimpleNamespace:
    return SimpleNamespace(
        id=3,
        owner_user_id=7,
        declared_area_sqm=Decimal(area),
        status="active",
    )


def _service() -> FarmPlotService:
    service = FarmPlotService(Mock())
    service.repo = Mock()
    return service


def test_plot_database_constraints_cover_area_coordinates_and_archive() -> None:
    names = {
        constraint.name
        for constraint in FarmPlot.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert {
        "ck_farm_plots_area_positive",
        "ck_farm_plots_coordinate_pair",
        "ck_farm_plots_latitude",
        "ck_farm_plots_longitude",
        "ck_farm_plots_status",
        "ck_farm_plots_archive_state",
    } <= names
    farm_checks = {
        constraint.name
        for constraint in Farm.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert "ck_farms_declared_area_positive" in farm_checks


def test_boundary_requires_closed_ring_and_three_distinct_points() -> None:
    points = [
        FarmGeoPoint(latitude=35, longitude=51),
        FarmGeoPoint(latitude=35, longitude=52),
        FarmGeoPoint(latitude=36, longitude=52),
    ]
    with pytest.raises(ValidationError):
        FarmPlotCreateIn(name="A", area_sqm=10, boundary=points + [points[1]])

    payload = FarmPlotCreateIn(
        name="A",
        area_sqm=10,
        boundary=points + [points[0]],
    )
    assert payload.boundary[0] == payload.boundary[-1]


def test_coordinate_pair_and_ranges_are_validated() -> None:
    with pytest.raises(ValidationError):
        FarmPlotCreateIn(name="A", area_sqm=10, latitude=35)
    with pytest.raises(ValidationError):
        FarmGeoPoint(latitude=91, longitude=51)


def test_total_plot_area_cannot_exceed_declared_farm_area() -> None:
    service = _service()
    service.repo.total_plot_area.return_value = Decimal("850")
    with pytest.raises(AppException) as exc_info:
        service._validate_area(_farm(), Decimal("151"))
    assert exc_info.value.code == "FARM_PLOT_AREA_EXCEEDS_FARM"
    assert exc_info.value.status_code == 409


def test_area_check_locks_owner_farm_before_mutation() -> None:
    service = _service()
    farm = _farm()
    service.repo.get_owned_for_update.return_value = farm
    service.repo.total_plot_area.return_value = Decimal("0")
    service.repo.add_plot.return_value = SimpleNamespace(
        id=5,
        farm_id=3,
        name="قطعه یک",
        description=None,
        area_sqm=Decimal("100"),
        province_id=None,
        county_id=None,
        district_id=None,
        rural_district_id=None,
        city_id=None,
        village_id=None,
        latitude=None,
        longitude=None,
        boundary=None,
        status="active",
        archived_at=None,
        archive_reason=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service.create(
        user=SimpleNamespace(id=7),
        farm_id=3,
        payload=FarmPlotCreateIn(name="قطعه یک", area_sqm=100),
    )
    service.repo.get_owned_for_update.assert_called_once_with(
        farm_id=3,
        owner_user_id=7,
    )


def test_geo_hierarchy_mismatch_is_rejected() -> None:
    service = _service()
    service.repo.get_province.return_value = SimpleNamespace(id=1)
    service.repo.get_county.return_value = SimpleNamespace(id=2, province_id=9)
    with pytest.raises(AppException) as exc_info:
        service._validate_geo({"province_id": 1, "county_id": 2})
    assert exc_info.value.code == "FARM_PLOT_GEO_MISMATCH"


def test_geo_children_require_explicit_parents() -> None:
    service = _service()
    with pytest.raises(AppException) as exc_info:
        service._validate_geo({"city_id": 4})
    assert exc_info.value.code == "FARM_PLOT_GEO_PARENT_REQUIRED"


def test_plot_routes_are_private_owner_routes() -> None:
    paths = app.openapi()["paths"]
    expected = {
        "/api/v1/farms/{farm_id}/plots",
        "/api/v1/farms/{farm_id}/plots/{plot_id}",
        "/api/v1/farms/{farm_id}/plots/{plot_id}/archive",
        "/api/v1/farms/{farm_id}/plots/{plot_id}/restore",
    }
    assert expected <= set(paths)
    assert not any("/public/farms" in path for path in paths)
