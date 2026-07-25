from sqlalchemy import CheckConstraint, UniqueConstraint

from app.modules.auth.seed import BASE_PERMISSIONS
from app.modules.farms.models import (
    FarmCrop,
    FarmCropCategory,
    FarmCropVariety,
    FarmMeasurementUnit,
)
from app.modules.farms.seed import CROP_CATEGORIES, CROPS, MEASUREMENT_UNITS


def _constraint_names(model, constraint_type) -> set[str | None]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, constraint_type)
    }


def test_farm_reference_tables_are_registered() -> None:
    assert FarmMeasurementUnit.__tablename__ == "farm_measurement_units"
    assert FarmCropCategory.__tablename__ == "farm_crop_categories"
    assert FarmCrop.__tablename__ == "farm_crops"
    assert FarmCropVariety.__tablename__ == "farm_crop_varieties"


def test_farm_reference_database_contracts_are_explicit() -> None:
    assert "ck_farm_measurement_units_factor_positive" in _constraint_names(
        FarmMeasurementUnit,
        CheckConstraint,
    )
    assert "ck_farm_crops_cycle_type" in _constraint_names(FarmCrop, CheckConstraint)
    assert "uq_farm_crops_scientific_name" in _constraint_names(
        FarmCrop,
        UniqueConstraint,
    )
    assert "uq_farm_crop_varieties_crop_code" in _constraint_names(
        FarmCropVariety,
        UniqueConstraint,
    )


def test_farm_reference_seed_catalog_is_consistent() -> None:
    unit_codes = {item.code for item in MEASUREMENT_UNITS}
    category_codes = {item.code for item in CROP_CATEGORIES}
    crop_codes = {item.code for item in CROPS}

    assert len(unit_codes) == len(MEASUREMENT_UNITS) == 8
    assert len(category_codes) == len(CROP_CATEGORIES) == 7
    assert len(crop_codes) == len(CROPS) == 13
    assert {item.category_code for item in CROPS} <= category_codes
    assert all(item.factor_to_base > 0 for item in MEASUREMENT_UNITS)
    assert {"area", "mass", "volume", "length", "count"} <= {
        item.dimension for item in MEASUREMENT_UNITS
    }


def test_farm_permissions_are_seeded() -> None:
    codes = {permission.code for permission in BASE_PERMISSIONS}
    assert {
        "farms.read_own",
        "farms.manage_own",
        "farms.admin_read",
        "farms.admin_manage",
        "farm_references.read",
        "farm_references.manage",
    } <= codes
