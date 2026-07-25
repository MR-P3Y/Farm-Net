from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint

from app.core.exceptions import AppException
from app.main import app
from app.modules.farms.enums import LabMetric, LabSubjectType
from app.modules.farms.models import (
    FarmIrrigationProfile,
    FarmLabObservation,
    FarmSoilProfile,
    FarmWaterSource,
)
from app.modules.farms.schemas import LabObservationCreateIn
from app.modules.farms.service import FarmEnvironmentService


def _checks(model):
    return {item.name for item in model.__table__.constraints if isinstance(item, CheckConstraint)}


def test_environment_database_contracts_are_registered() -> None:
    assert "ck_farm_soil_profiles_depth_positive" in _checks(FarmSoilProfile)
    assert "ck_farm_water_sources_archive_state" in _checks(FarmWaterSource)
    assert "ck_farm_irrigation_profiles_efficiency" in _checks(FarmIrrigationProfile)
    assert "ck_farm_lab_observations_exact_subject" in _checks(FarmLabObservation)
    assert "ck_farm_lab_observations_dates" in _checks(FarmLabObservation)


def test_lab_dates_and_nonnegative_values_are_validated() -> None:
    with pytest.raises(ValidationError):
        LabObservationCreateIn(
            subject_type=LabSubjectType.SOIL,
            subject_id=1,
            metric_code=LabMetric.PH,
            value=Decimal("7"),
            unit_code="ph",
            sampled_on=date(2026, 2, 2),
            tested_on=date(2026, 2, 1),
        )


def test_metric_subject_and_canonical_unit_are_enforced() -> None:
    service = FarmEnvironmentService(Mock())
    service.repo = Mock()
    service.plot_service.repo = service.repo
    service.repo.get_water_source.return_value = SimpleNamespace(id=3)
    payload = LabObservationCreateIn(
        subject_type=LabSubjectType.WATER,
        subject_id=3,
        metric_code=LabMetric.ORGANIC_MATTER,
        value=Decimal("2"),
        unit_code="percent",
        sampled_on=date(2026, 2, 1),
    )
    with pytest.raises(AppException) as exc_info:
        service.create_observation(user=SimpleNamespace(id=7), farm_id=1, payload=payload)
    assert exc_info.value.code == "FARM_LAB_METRIC_SUBJECT_INVALID"


def test_environment_routes_remain_private() -> None:
    paths = app.openapi()["paths"]
    assert "/api/v1/farms/{farm_id}/plots/{plot_id}/soil-profile" in paths
    assert "/api/v1/farms/{farm_id}/plots/{plot_id}/irrigation-profile" in paths
    assert "/api/v1/farms/{farm_id}/water-sources" in paths
    assert "/api/v1/farms/{farm_id}/lab-observations" in paths
    assert not any("/public/farms" in path for path in paths)
