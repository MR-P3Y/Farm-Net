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
from app.modules.rentals.service import RentalService


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
