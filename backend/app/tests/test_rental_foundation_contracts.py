from types import SimpleNamespace
from unittest.mock import Mock
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.modules.auth.seed import BASE_PERMISSIONS
from app.modules.rentals.enums import (
    LessorStatus,
    RentalEquipmentStatus,
    RentalOperatorMode,
    RentalRequestStatus,
)
from app.modules.rentals.models import (
    LessorProfile,
    RentalAvailabilityBlock,
    RentalCategory,
    RentalEquipment,
    RentalEquipmentMedia,
    RentalPricingRule,
    RentalRequest,
    RentalRequestStatusLog,
)
from app.modules.rentals.schemas import RentalCategoryCreateIn, RentalCategoryUpdateIn
from app.modules.rentals.schemas import (
    RentalAvailabilityBlockIn,
    RentalEquipmentInput,
    RentalEquipmentMediaIn,
    RentalPricingRuleIn,
)
from app.modules.rentals.service import RentalService
from app.modules.auth.exceptions import ValidationAuthError


def test_rental_foundation_has_all_independent_tables() -> None:
    tables = {
        model.__tablename__
        for model in (
            RentalCategory,
            LessorProfile,
            RentalEquipment,
            RentalEquipmentMedia,
            RentalPricingRule,
            RentalAvailabilityBlock,
            RentalRequest,
            RentalRequestStatusLog,
        )
    }
    assert tables == {
        "rental_categories",
        "rental_lessor_profiles",
        "rental_equipment",
        "rental_equipment_media",
        "rental_pricing_rules",
        "rental_availability_blocks",
        "rental_requests",
        "rental_request_status_logs",
    }


def test_rental_database_contracts_protect_identity_ranges_and_exact_once_logs() -> None:
    equipment_uniques = {
        constraint.name
        for constraint in RentalEquipment.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    request_checks = {
        constraint.name
        for constraint in RentalRequest.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    availability_checks = {
        constraint.name
        for constraint in RentalAvailabilityBlock.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "uq_rental_equipment_lessor_slug" in equipment_uniques
    assert "ck_rental_request_valid_range" in request_checks
    assert "ck_rental_request_units_positive" in request_checks
    assert "ck_rental_availability_valid_range" in availability_checks
    assert RentalRequestStatusLog.__table__.c.event_key.unique is True


def test_rental_enums_and_permissions_cover_owner_requester_and_admin() -> None:
    assert {status.value for status in RentalRequestStatus} == {
        "pending",
        "accepted",
        "in_progress",
        "completed",
        "cancelled",
        "rejected",
    }
    assert RentalOperatorMode.EITHER.value == "either"
    assert LessorStatus.DRAFT.value == "draft"
    assert RentalEquipmentStatus.ARCHIVED.value == "archived"

    permission_codes = {permission.code for permission in BASE_PERMISSIONS}
    assert {
        "rental_categories.admin_read",
        "rental_lessors.profile_manage",
        "rental_lessors.admin_moderate",
        "rental_equipment.create",
        "rental_equipment.manage_pricing",
        "rental_equipment.manage_availability",
        "rental_equipment.admin_read",
        "rental_requests.create",
        "rental_requests.manage_assigned",
        "rental_requests.admin_manage",
    } <= permission_codes


def test_rental_category_contract_normalizes_code_and_supports_parent_clear() -> None:
    created = RentalCategoryCreateIn(code=" tractors ", title=" تراکتور ")
    cleared = RentalCategoryUpdateIn.model_validate({"parent_id": None})

    assert created.code == "tractors"
    assert created.title == "تراکتور"
    assert cleared.model_dump(exclude_unset=True) == {"parent_id": None}


def test_rental_default_taxonomy_has_stable_unique_codes() -> None:
    codes = [code for code, _ in RentalService.DEFAULT_CATEGORIES]

    assert len(codes) == 8
    assert len(codes) == len(set(codes))
    assert {"tractors", "harvesters", "sprayers", "irrigation"} <= set(codes)


def test_equipment_input_carries_operator_location_and_media_contracts() -> None:
    payload = RentalEquipmentInput(
        category_id=1,
        title="تراکتور رومانی",
        slug="romanian-tractor",
        operator_mode="either",
        province_id=1,
        city_id=2,
        media_items=[RentalEquipmentMediaIn(media_file_id=9)],
    )

    assert payload.operator_mode == "either"
    assert payload.media_items[0].media_file_id == 9
    assert payload.currency == "TOMAN"


def test_equipment_media_requires_active_public_owner_file_and_assigns_primary() -> None:
    service = RentalService.__new__(RentalService)
    service.repo = Mock()
    service.repo.get_media.return_value = SimpleNamespace(
        owner_user_id=7,
        status="active",
        visibility="public",
    )

    rows = service._media_rows([RentalEquipmentMediaIn(media_file_id=3)], owner_user_id=7)

    assert rows[0].is_primary is True

    service.repo.get_media.return_value.owner_user_id = 8
    with pytest.raises(ValidationAuthError):
        service._media_rows([RentalEquipmentMediaIn(media_file_id=3)], owner_user_id=7)


def test_equipment_filter_rejects_unknown_operator_mode() -> None:
    service = RentalService.__new__(RentalService)

    with pytest.raises(ValidationAuthError):
        service._validate_equipment_filters({"operator_mode": "sometimes"})


def test_pricing_rule_enforces_operator_compatibility() -> None:
    service = RentalService.__new__(RentalService)
    with_operator = RentalPricingRuleIn(
        unit="day", operator_included=True, price_amount=Decimal("2500000")
    )

    row = service._pricing_row(with_operator, "with_operator")
    assert row.operator_included is True

    with pytest.raises(ValidationAuthError):
        service._pricing_row(with_operator, "without_operator")


def test_pricing_rule_rejects_unknown_unit() -> None:
    service = RentalService.__new__(RentalService)
    payload = RentalPricingRuleIn(unit="month", price_amount=Decimal("1"))

    with pytest.raises(ValidationAuthError):
        service._pricing_row(payload, "either")


def test_availability_range_normalizes_aware_datetimes_and_rejects_reverse_range() -> None:
    service = RentalService.__new__(RentalService)
    start = datetime.now(UTC)
    end = start + timedelta(days=1)

    normalized_start, normalized_end = service._valid_range(start, end)
    assert normalized_start.tzinfo is None
    assert normalized_end.tzinfo is None

    with pytest.raises(ValidationAuthError):
        service._valid_range(end, start)


def test_availability_contract_supports_only_explicit_block_types() -> None:
    start = datetime.now(UTC)
    payload = RentalAvailabilityBlockIn(
        block_type="maintenance", starts_at=start, ends_at=start + timedelta(hours=2)
    )
    service = RentalService.__new__(RentalService)

    service._validate_block_type(payload.block_type)
    with pytest.raises(ValidationAuthError):
        service._validate_block_type("booked_elsewhere")
