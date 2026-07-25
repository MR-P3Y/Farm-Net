from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy import CheckConstraint

from app.core.exceptions import AppException
from app.main import app
from app.modules.farms.diary_service import FarmDiaryService
from app.modules.farms.enums import FarmOperationType
from app.modules.farms.models import (
    FarmHarvestObservation,
    FarmOperation,
    FarmOperationInput,
    FarmRecordMedia,
)
from app.modules.farms.schemas import FarmHarvestCreateIn


def _checks(model):
    return {
        item.name
        for item in model.__table__.constraints
        if isinstance(item, CheckConstraint)
    }


def test_diary_database_contracts_are_registered() -> None:
    assert "ck_farm_operations_type" in _checks(FarmOperation)
    assert "ck_farm_operation_inputs_quantity_positive" in _checks(FarmOperationInput)
    assert "ck_farm_harvest_quantity_positive" in _checks(FarmHarvestObservation)
    assert "ck_farm_record_media_exact_subject" in _checks(FarmRecordMedia)


def test_operation_type_contract_is_explicit() -> None:
    assert {item.value for item in FarmOperationType} == {
        "land_preparation", "planting", "irrigation", "fertilizing",
        "spraying", "weeding", "pruning", "monitoring", "other",
    }


def test_harvest_rejects_non_mass_or_count_unit() -> None:
    service = FarmDiaryService(Mock())
    service._active_cycle = Mock(return_value=SimpleNamespace(
        id=9, actual_start_date=date(2026, 1, 1)
    ))
    service._unit = Mock(return_value=SimpleNamespace(id=4, dimension="volume"))
    payload = FarmHarvestCreateIn(
        harvested_on=date(2026, 2, 1),
        quantity=Decimal("25"),
        measurement_unit_id=4,
    )

    with pytest.raises(AppException) as exc_info:
        service.create_harvest(
            user=SimpleNamespace(id=1), farm_id=2, plot_id=3,
            cycle_id=9, payload=payload,
        )

    assert exc_info.value.code == "FARM_HARVEST_UNIT_INVALID"


def test_diary_rejects_non_active_cycle() -> None:
    service = FarmDiaryService(Mock())
    service.cycles._cycle = Mock(return_value=SimpleNamespace(status="completed"))

    with pytest.raises(AppException) as exc_info:
        service._active_cycle(1, 2, 3, 4)

    assert exc_info.value.code == "FARM_CROP_CYCLE_NOT_ACTIVE"


def test_diary_routes_are_owner_private_contracts() -> None:
    paths = app.openapi()["paths"]
    root = "/api/v1/farms/{farm_id}/plots/{plot_id}/cycles/{cycle_id}"
    assert f"{root}/operations" in paths
    assert f"{root}/operations/{{operation_id}}/inputs" in paths
    assert f"{root}/harvests" in paths
    assert f"{root}/media" in paths
    assert not any("/public/farms" in path for path in paths)
