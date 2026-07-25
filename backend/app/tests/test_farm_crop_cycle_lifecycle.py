from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint

from app.core.exceptions import AppException
from app.main import app
from app.modules.farms.enums import CultivationMode
from app.modules.farms.models import FarmCropCycle
from app.modules.farms.schemas import FarmCropCycleCreateIn
from app.modules.farms.service import FarmCropCycleService


def _service() -> FarmCropCycleService:
    service = FarmCropCycleService(Mock())
    service.repo = Mock()
    service.plot_service.repo = service.repo
    return service


def test_cycle_database_contracts_cover_dates_status_and_mode() -> None:
    names = {
        item.name
        for item in FarmCropCycle.__table__.constraints
        if isinstance(item, CheckConstraint)
    }
    assert {
        "ck_farm_crop_cycles_planned_dates",
        "ck_farm_crop_cycles_actual_dates",
        "ck_farm_crop_cycles_lifecycle_dates",
        "ck_farm_crop_cycles_cultivation_mode",
        "ck_farm_crop_cycles_status",
    } <= names


def test_planned_dates_are_ordered() -> None:
    with pytest.raises(ValidationError):
        FarmCropCycleCreateIn(
            crop_id=1,
            planned_start_date=date(2026, 5, 2),
            planned_end_date=date(2026, 5, 1),
        )


def test_variety_must_belong_to_selected_crop() -> None:
    service = _service()
    service.repo.get_crop.return_value = SimpleNamespace(id=2)
    service.repo.get_variety.return_value = SimpleNamespace(id=5, crop_id=9)
    with pytest.raises(AppException) as exc_info:
        service._validate_reference(2, 5)
    assert exc_info.value.code == "FARM_CROP_VARIETY_MISMATCH"


def test_single_crop_overlap_is_rejected() -> None:
    service = _service()
    service.repo.overlapping_cycles.return_value = [
        SimpleNamespace(cultivation_mode=CultivationMode.SINGLE.value)
    ]
    with pytest.raises(AppException) as exc_info:
        service._validate_overlap(
            plot_id=2,
            starts_on=date(2026, 1, 1),
            ends_on=date(2026, 2, 1),
            mode=CultivationMode.SINGLE.value,
        )
    assert exc_info.value.code == "FARM_CROP_CYCLE_OVERLAP"


def test_overlap_requires_intercrop_on_every_conflicting_cycle() -> None:
    service = _service()
    service.repo.overlapping_cycles.return_value = [
        SimpleNamespace(cultivation_mode=CultivationMode.INTERCROP.value)
    ]
    service._validate_overlap(
        plot_id=2,
        starts_on=date(2026, 1, 1),
        ends_on=date(2026, 2, 1),
        mode=CultivationMode.INTERCROP.value,
    )


def test_cycle_and_reference_routes_are_private() -> None:
    paths = app.openapi()["paths"]
    assert "/api/v1/farm-references/crops" in paths
    assert "/api/v1/farms/{farm_id}/plots/{plot_id}/cycles" in paths
    assert (
        "/api/v1/farms/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/complete"
        in paths
    )
    assert not any("/public/farms" in path for path in paths)
