import re
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.finance.rental_service import (
    RentalFinancialContractError,
    RentalFinancialService,
)
from app.modules.media.enums import MediaStatus, MediaVisibility
from app.modules.notifications.enums import NotificationEventType, NotificationPriority
from app.modules.notifications.service import NotificationService
from app.modules.profiles.enums import VerificationStatus, VerificationTargetRole
from app.modules.profiles.models import VerificationRequest
from app.modules.rentals.enums import (
    LessorStatus,
    RentalDiscoverySort,
    RentalAvailabilityBlockType,
    RentalEquipmentStatus,
    RentalOperatorMode,
    RentalPricingUnit,
    RentalRequestStatus,
)
from app.modules.rentals.models import (
    LessorProfile,
    RentalCategory,
    RentalEquipment,
    RentalEquipmentMedia,
    RentalAvailabilityBlock,
    RentalPricingRule,
    RentalRequest,
    RentalRequestStatusLog,
)
from app.modules.rentals.repository import RentalRepository
from app.modules.rentals.schemas import (
    RentalCategoryCreateIn,
    RentalCategoryOut,
    RentalCategoryUpdateIn,
    LessorProfileInput,
    LessorProfileOut,
    RentalEquipmentInput,
    RentalEquipmentMediaOut,
    RentalEquipmentOut,
    RentalEquipmentPublicOut,
    RentalAvailabilityBlockIn,
    RentalAvailabilityBlockOut,
    RentalAvailabilityCheckOut,
    RentalPricingRuleIn,
    RentalPricingRuleOut,
    RentalRequestAdminDetailOut,
    RentalRequestCancelIn,
    RentalRequestCreateIn,
    RentalRequestDetailOut,
    RentalRequestListOut,
    RentalRequestStatusLogOut,
    RentalRequestStatusIn,
)


class RentalService:
    LESSOR_REQUEST_TRANSITIONS = {
        "pending": {"accepted", "rejected"},
        "accepted": {"in_progress"},
        "in_progress": {"completed"},
    }
    ADMIN_REQUEST_TRANSITIONS = {
        "pending": {"accepted", "rejected", "cancelled"},
        "accepted": {"in_progress", "cancelled"},
        "in_progress": {"completed", "cancelled"},
    }
    DEFAULT_CATEGORIES = (
        ("tractors", "تراکتور و ماشین‌های کشاورزی"),
        ("harvesters", "کمباین و تجهیزات برداشت"),
        ("tillage", "ادوات خاک‌ورزی و شخم"),
        ("planting", "تجهیزات کاشت"),
        ("sprayers", "سم‌پاش و محلول‌پاش"),
        ("irrigation", "تجهیزات آبیاری"),
        ("transport", "تریلر و تجهیزات حمل"),
        ("greenhouse", "تجهیزات گلخانه‌ای"),
    )

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RentalRepository(db)

    def seed_categories(self) -> list[RentalCategoryOut]:
        rows = []
        for order, (code, title) in enumerate(self.DEFAULT_CATEGORIES, start=1):
            row = self.repo.get_category_by_code(code)
            if row is None:
                row = RentalCategory(code=code, title=title, sort_order=order * 100, is_active=True)
                self.db.add(row)
                self.db.flush()
            rows.append(row)
        self.db.commit()
        return [self._category_out(row) for row in rows]

    def list_categories(self, *, active_only: bool, q: str | None) -> list[RentalCategoryOut]:
        return [
            self._category_out(row)
            for row in self.repo.list_categories(active_only=active_only, q=q)
        ]

    def create_category(self, payload: RentalCategoryCreateIn) -> RentalCategoryOut:
        if payload.parent_id:
            self._require_category(payload.parent_id)
        row = RentalCategory(**payload.model_dump())
        self.db.add(row)
        self._commit_unique("Rental category code already exists")
        return self._category_out(row)

    def update_category(
        self, category_id: int, payload: RentalCategoryUpdateIn
    ) -> RentalCategoryOut:
        row = self._require_category(category_id)
        values = payload.model_dump(exclude_unset=True)
        if "parent_id" in values:
            self._validate_parent(category_id, values["parent_id"])
        for field, value in values.items():
            setattr(row, field, value)
        self._commit_unique("Rental category code already exists")
        return self._category_out(row)

    def get_my_profile(self, user: AuthUser) -> LessorProfileOut | None:
        row = self.repo.get_profile_by_user(user.id)
        return self._profile_out(row) if row else None

    def save_my_profile(self, user: AuthUser, payload: LessorProfileInput) -> LessorProfileOut:
        row = self.repo.get_profile_by_user(user.id)
        if row is None:
            row = LessorProfile(user_id=user.id)
            self.db.add(row)
        if row.status in {
            LessorStatus.PENDING_REVIEW.value,
            LessorStatus.APPROVED.value,
            LessorStatus.SUSPENDED.value,
        }:
            raise ValidationAuthError(
                message="Lessor profile cannot be edited in current status",
                details={"status": row.status},
            )
        for field, value in payload.model_dump().items():
            setattr(row, field, value)
        self.db.commit()
        self.db.refresh(row)
        return self._profile_out(row)

    def submit_my_profile(self, user: AuthUser) -> LessorProfileOut:
        row = self.repo.get_profile_by_user(user.id)
        if row is None:
            raise ValidationAuthError(message="Lessor profile not found")
        if row.status not in {LessorStatus.DRAFT.value, LessorStatus.REJECTED.value}:
            raise ValidationAuthError(
                message="Lessor profile cannot be submitted in current status",
                details={"status": row.status},
            )
        missing = [
            name
            for name in ("display_name", "phone", "province_id", "city_id", "address_text")
            if not getattr(row, name)
        ]
        if missing:
            raise ValidationAuthError(
                message="Lessor profile is incomplete", details={"missing_fields": missing}
            )
        row.status = LessorStatus.PENDING_REVIEW.value
        row.submitted_at = self._now()
        row.admin_note = None
        self.db.commit()
        self.db.refresh(row)
        return self._profile_out(row)

    def list_admin_profiles(self, **filters) -> tuple[list[LessorProfileOut], int]:
        rows, total = self.repo.list_profiles(**filters)
        return [self._profile_out(row) for row in rows], total

    def moderate_profile(
        self, profile_id: int, *, status: str, admin_note: str | None, admin_user: AuthUser
    ) -> LessorProfileOut:
        allowed = {
            LessorStatus.APPROVED.value,
            LessorStatus.REJECTED.value,
            LessorStatus.SUSPENDED.value,
            LessorStatus.PENDING_REVIEW.value,
        }
        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid lessor profile status", details={"status": status}
            )
        row = self.repo.get_profile(profile_id)
        if row is None:
            raise ValidationAuthError(
                message="Lessor profile not found", details={"profile_id": profile_id}
            )
        if status in {LessorStatus.REJECTED.value, LessorStatus.SUSPENDED.value} and not admin_note:
            raise ValidationAuthError(message="Admin note is required for this status")
        if (
            status == LessorStatus.APPROVED.value
            and row.status != LessorStatus.PENDING_REVIEW.value
        ):
            raise ValidationAuthError(message="Only pending lessor profiles can be approved")
        if status == LessorStatus.APPROVED.value:
            verified = (
                self.db.query(VerificationRequest.id)
                .filter(
                    VerificationRequest.user_id == row.user_id,
                    VerificationRequest.target_role == VerificationTargetRole.LESSOR.value,
                    VerificationRequest.status == VerificationStatus.APPROVED.value,
                )
                .first()
            )
            if verified is None:
                raise ValidationAuthError(
                    message="Approved lessor verification is required",
                    details={"user_id": row.user_id},
                )
        row.status = status
        row.admin_note = admin_note
        if status == LessorStatus.APPROVED.value:
            row.approved_at = self._now()
            row.approved_by = admin_user.id
        self.db.commit()
        self.db.refresh(row)
        return self._profile_out(row)

    def list_public_equipment(self, **filters) -> tuple[list[RentalEquipmentPublicOut], int]:
        self._validate_equipment_filters(filters)
        rows, total = self.repo.list_equipment(public=True, **filters)
        return [self._public_equipment_out(row) for row in rows], total

    def get_public_equipment(self, equipment_id: int) -> RentalEquipmentPublicOut:
        row = self.repo.get_public_equipment(equipment_id)
        if row is None:
            raise ValidationAuthError(
                message="Rental equipment not found", details={"equipment_id": equipment_id}
            )
        return self._public_equipment_out(row)

    def list_my_equipment(self, user: AuthUser, **filters) -> tuple[list[RentalEquipmentOut], int]:
        profile = self._approved_lessor(user)
        self._validate_equipment_filters(filters)
        rows, total = self.repo.list_equipment(
            public=False, lessor_profile_id=profile.id, **filters
        )
        return [self._equipment_out(row) for row in rows], total

    def create_my_equipment(
        self, user: AuthUser, payload: RentalEquipmentInput
    ) -> RentalEquipmentOut:
        profile = self._approved_lessor(user)
        values = self._equipment_values(payload)
        media_items = values.pop("media_items")
        row = RentalEquipment(
            lessor_profile_id=profile.id,
            status=RentalEquipmentStatus.DRAFT.value,
            admin_note=None,
            **values,
        )
        self.db.add(row)
        self.db.flush()
        self.repo.replace_equipment_media(row, self._media_rows(media_items, user.id))
        self._commit_unique("Rental equipment slug already exists for this lessor")
        return self._equipment_out(self.repo.get_equipment(row.id))

    def update_my_equipment(
        self, user: AuthUser, equipment_id: int, payload: RentalEquipmentInput
    ) -> RentalEquipmentOut:
        profile = self._approved_lessor(user)
        row = self._owned_equipment(profile.id, equipment_id)
        if row.status not in {
            RentalEquipmentStatus.DRAFT.value,
            RentalEquipmentStatus.REJECTED.value,
        }:
            raise ValidationAuthError(
                message="Rental equipment cannot be edited in current status",
                details={"status": row.status},
            )
        values = self._equipment_values(payload)
        media_items = values.pop("media_items")
        for field, value in values.items():
            setattr(row, field, value)
        self.repo.replace_equipment_media(row, self._media_rows(media_items, user.id))
        self._commit_unique("Rental equipment slug already exists for this lessor")
        return self._equipment_out(self.repo.get_equipment(row.id))

    def submit_my_equipment(self, user: AuthUser, equipment_id: int) -> RentalEquipmentOut:
        profile = self._approved_lessor(user)
        row = self._owned_equipment(profile.id, equipment_id)
        if row.status not in {
            RentalEquipmentStatus.DRAFT.value,
            RentalEquipmentStatus.REJECTED.value,
        }:
            raise ValidationAuthError(
                message="Rental equipment cannot be submitted in current status",
                details={"status": row.status},
            )
        missing = [
            name
            for name in (
                "category_id",
                "title",
                "description",
                "province_id",
                "city_id",
                "address_text",
            )
            if not getattr(row, name)
        ]
        if not row.media:
            missing.append("media_items")
        if missing:
            raise ValidationAuthError(
                message="Rental equipment is incomplete", details={"missing_fields": missing}
            )
        row.status = RentalEquipmentStatus.PENDING_REVIEW.value
        row.submitted_at = self._now()
        row.admin_note = None
        self.db.commit()
        self.db.refresh(row)
        return self._equipment_out(self.repo.get_equipment(row.id))

    def list_admin_equipment(self, **filters) -> tuple[list[RentalEquipmentOut], int]:
        self._validate_equipment_filters(filters)
        rows, total = self.repo.list_equipment(public=False, **filters)
        return [self._equipment_out(row) for row in rows], total

    def moderate_equipment(
        self, equipment_id: int, *, status: str, admin_note: str | None, admin_user: AuthUser
    ) -> RentalEquipmentOut:
        allowed = {
            RentalEquipmentStatus.APPROVED.value,
            RentalEquipmentStatus.REJECTED.value,
            RentalEquipmentStatus.SUSPENDED.value,
            RentalEquipmentStatus.PENDING_REVIEW.value,
        }
        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid rental equipment status", details={"status": status}
            )
        row = self.repo.get_equipment(equipment_id)
        if row is None:
            raise ValidationAuthError(
                message="Rental equipment not found", details={"equipment_id": equipment_id}
            )
        if (
            status == RentalEquipmentStatus.APPROVED.value
            and row.status != RentalEquipmentStatus.PENDING_REVIEW.value
        ):
            raise ValidationAuthError(message="Only pending rental equipment can be approved")
        if status == RentalEquipmentStatus.APPROVED.value:
            if not row.media:
                raise ValidationAuthError(message="Rental equipment media is required for approval")
            if not self.repo.list_pricing_rules(row.id, active_only=True):
                raise ValidationAuthError(message="Active rental pricing is required for approval")
        if (
            status in {RentalEquipmentStatus.REJECTED.value, RentalEquipmentStatus.SUSPENDED.value}
            and not admin_note
        ):
            raise ValidationAuthError(message="Admin note is required for this status")
        row.status = status
        row.admin_note = admin_note
        if status == RentalEquipmentStatus.APPROVED.value:
            row.approved_at = self._now()
            row.approved_by = admin_user.id
        self.db.commit()
        self.db.refresh(row)
        return self._equipment_out(self.repo.get_equipment(row.id))

    def get_public_pricing(self, equipment_id: int) -> list[RentalPricingRuleOut]:
        self.get_public_equipment(equipment_id)
        return [
            self._pricing_out(row)
            for row in self.repo.list_pricing_rules(equipment_id, active_only=True)
        ]

    def replace_my_pricing(
        self, user: AuthUser, equipment_id: int, payloads: list[RentalPricingRuleIn]
    ) -> list[RentalPricingRuleOut]:
        profile = self._approved_lessor(user)
        equipment = self._owned_equipment(profile.id, equipment_id)
        equipment = self.repo.lock_equipment(equipment.id)
        if equipment.status in {
            RentalEquipmentStatus.SUSPENDED.value,
            RentalEquipmentStatus.ARCHIVED.value,
        }:
            raise ValidationAuthError(
                message="Rental pricing cannot be changed in current equipment status"
            )
        if not payloads:
            raise ValidationAuthError(message="At least one rental pricing rule is required")
        keys = [(item.unit, item.operator_included) for item in payloads]
        if len(keys) != len(set(keys)):
            raise ValidationAuthError(message="Duplicate rental pricing unit/operator rule")
        self.repo.replace_pricing_rules(
            equipment.id, [self._pricing_row(item, equipment.operator_mode) for item in payloads]
        )
        self.db.commit()
        return [self._pricing_out(row) for row in self.repo.list_pricing_rules(equipment.id)]

    def list_my_pricing(self, user: AuthUser, equipment_id: int) -> list[RentalPricingRuleOut]:
        profile = self._approved_lessor(user)
        equipment = self._owned_equipment(profile.id, equipment_id)
        return [self._pricing_out(row) for row in self.repo.list_pricing_rules(equipment.id)]

    def check_public_availability(
        self, equipment_id: int, starts_at: datetime, ends_at: datetime
    ) -> RentalAvailabilityCheckOut:
        self.get_public_equipment(equipment_id)
        starts_at, ends_at = self._valid_range(starts_at, ends_at)
        blocks = self.repo.list_availability_blocks(
            equipment_id, starts_at=starts_at, ends_at=ends_at
        )
        booking_overlap = self.repo.has_booking_overlap(equipment_id, starts_at, ends_at)
        return RentalAvailabilityCheckOut(
            equipment_id=equipment_id,
            starts_at=starts_at,
            ends_at=ends_at,
            is_available=not blocks and not booking_overlap,
            conflicting_blocks=[self._block_out(row, include_note=False) for row in blocks],
        )

    def list_my_availability(
        self, user: AuthUser, equipment_id: int
    ) -> list[RentalAvailabilityBlockOut]:
        profile = self._approved_lessor(user)
        equipment = self._owned_equipment(profile.id, equipment_id)
        return [self._block_out(row) for row in self.repo.list_availability_blocks(equipment.id)]

    def create_my_availability(
        self, user: AuthUser, equipment_id: int, payload: RentalAvailabilityBlockIn
    ) -> RentalAvailabilityBlockOut:
        profile = self._approved_lessor(user)
        equipment = self._owned_equipment(profile.id, equipment_id)
        equipment = self.repo.lock_equipment(equipment.id)
        starts_at, ends_at = self._valid_range(payload.starts_at, payload.ends_at)
        self._validate_block_type(payload.block_type)
        if self.repo.list_availability_blocks(
            equipment.id, starts_at=starts_at, ends_at=ends_at
        ) or self.repo.has_booking_overlap(equipment.id, starts_at, ends_at):
            raise ValidationAuthError(
                message="Rental availability range overlaps an existing block or booking"
            )
        row = RentalAvailabilityBlock(
            equipment_id=equipment.id,
            block_type=payload.block_type,
            starts_at=starts_at,
            ends_at=ends_at,
            note=payload.note,
            created_by=user.id,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._block_out(row)

    def update_my_availability(
        self, user: AuthUser, equipment_id: int, block_id: int, payload: RentalAvailabilityBlockIn
    ) -> RentalAvailabilityBlockOut:
        profile = self._approved_lessor(user)
        equipment = self._owned_equipment(profile.id, equipment_id)
        equipment = self.repo.lock_equipment(equipment.id)
        row = self.repo.get_availability_block(block_id)
        if row is None or row.equipment_id != equipment.id:
            raise ValidationAuthError(message="Rental availability block not found")
        starts_at, ends_at = self._valid_range(payload.starts_at, payload.ends_at)
        self._validate_block_type(payload.block_type)
        conflicts = [
            item
            for item in self.repo.list_availability_blocks(
                equipment.id, starts_at=starts_at, ends_at=ends_at
            )
            if item.id != row.id
        ]
        if conflicts or self.repo.has_booking_overlap(equipment.id, starts_at, ends_at):
            raise ValidationAuthError(
                message="Rental availability range overlaps an existing block or booking"
            )
        row.block_type, row.starts_at, row.ends_at, row.note = (
            payload.block_type,
            starts_at,
            ends_at,
            payload.note,
        )
        self.db.commit()
        self.db.refresh(row)
        return self._block_out(row)

    def delete_my_availability(self, user: AuthUser, equipment_id: int, block_id: int) -> None:
        profile = self._approved_lessor(user)
        equipment = self._owned_equipment(profile.id, equipment_id)
        equipment = self.repo.lock_equipment(equipment.id)
        row = self.repo.get_availability_block(block_id)
        if row is None or row.equipment_id != equipment.id:
            raise ValidationAuthError(message="Rental availability block not found")
        self.db.delete(row)
        self.db.commit()

    def _approved_lessor(self, user: AuthUser) -> LessorProfile:
        profile = self.repo.get_profile_by_user(user.id)
        if profile is None or profile.status != LessorStatus.APPROVED.value:
            raise ValidationAuthError(message="Approved lessor profile is required")
        return profile

    def _owned_equipment(self, profile_id: int, equipment_id: int) -> RentalEquipment:
        row = self.repo.get_equipment(equipment_id)
        if row is None or row.lessor_profile_id != profile_id:
            raise ValidationAuthError(
                message="Rental equipment not found", details={"equipment_id": equipment_id}
            )
        return row

    def _equipment_values(self, payload: RentalEquipmentInput) -> dict:
        if payload.category_id is not None:
            category = self._require_category(payload.category_id)
            if not category.is_active:
                raise ValidationAuthError(message="Rental category is inactive")
        if payload.operator_mode not in {item.value for item in RentalOperatorMode}:
            raise ValidationAuthError(
                message="Invalid rental operator mode",
                details={"operator_mode": payload.operator_mode},
            )
        slug = payload.slug.strip().lower().replace(" ", "-")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,178}[a-z0-9]", slug):
            raise ValidationAuthError(message="Invalid rental equipment slug")
        values = payload.model_dump()
        values["slug"] = slug
        values["currency"] = payload.currency.upper()
        if payload.security_deposit_amount is not None:
            values["security_deposit_amount"] = Decimal(str(payload.security_deposit_amount))
        return values

    def _media_rows(self, items, owner_user_id: int) -> list[RentalEquipmentMedia]:
        if sum(1 for item in items if item.is_primary) > 1:
            raise ValidationAuthError(
                message="Only one primary rental equipment media item is allowed"
            )
        rows = []
        for item in items:
            media = self.repo.get_media(item.media_file_id)
            if (
                media is None
                or media.owner_user_id != owner_user_id
                or media.status != MediaStatus.ACTIVE.value
                or media.visibility != MediaVisibility.PUBLIC.value
            ):
                raise ValidationAuthError(
                    message="Active public owner media is required",
                    details={"media_file_id": item.media_file_id},
                )
            rows.append(
                RentalEquipmentMedia(
                    media_file_id=item.media_file_id,
                    sort_order=item.sort_order,
                    is_primary=item.is_primary,
                    alt_text=item.alt_text,
                )
            )
        if rows and not any(row.is_primary for row in rows):
            rows[0].is_primary = True
        return rows

    def create_request(
        self, user: AuthUser, payload: RentalRequestCreateIn
    ) -> RentalRequestDetailOut:
        equipment = self.repo.get_public_equipment(payload.equipment_id)
        if equipment is None:
            raise ValidationAuthError(message="Rental equipment not found")
        if equipment.lessor_profile.user_id == user.id:
            raise ValidationAuthError(message="Lessor cannot rent own equipment")
        pricing = self.repo.get_pricing_rule(payload.pricing_rule_id)
        if pricing is None or pricing.equipment_id != equipment.id or not pricing.is_active:
            raise ValidationAuthError(message="Active rental pricing rule not found")
        starts_at, ends_at = self._valid_range(payload.starts_at, payload.ends_at)
        if payload.requested_units < pricing.minimum_units:
            raise ValidationAuthError(
                message="Requested units are below pricing minimum",
                details={"minimum_units": str(pricing.minimum_units)},
            )
        if payload.operator_requested != pricing.operator_included:
            raise ValidationAuthError(message="Requested operator mode does not match pricing rule")
        if self.repo.list_availability_blocks(
            equipment.id, starts_at=starts_at, ends_at=ends_at
        ) or self.repo.has_booking_overlap(equipment.id, starts_at, ends_at):
            raise ValidationAuthError(
                message="Rental equipment is not available for requested range"
            )
        row = RentalRequest(
            requester_user_id=user.id,
            lessor_profile_id=equipment.lessor_profile_id,
            equipment_id=equipment.id,
            pricing_rule_id=pricing.id,
            starts_at=starts_at,
            ends_at=ends_at,
            requested_units=payload.requested_units,
            operator_requested=payload.operator_requested,
            status=RentalRequestStatus.PENDING.value,
            currency=pricing.currency,
            delivery_address=payload.delivery_address,
            requester_note=payload.requester_note,
        )
        self.db.add(row)
        self.db.flush()
        self.db.add(
            RentalRequestStatusLog(
                request_id=row.id,
                changed_by=user.id,
                from_status=None,
                to_status=row.status,
                note=None,
                event_key=f"rental_request:{row.id}:created",
            )
        )
        self._notify_request_created(row, actor_user_id=user.id)
        self.db.commit()
        return self._request_detail(self.repo.get_request(row.id))

    def list_my_requests(self, user: AuthUser, **filters) -> tuple[list[RentalRequestListOut], int]:
        self._validate_request_status_filter(filters.get("status"))
        rows, total = self.repo.list_requests(requester_user_id=user.id, **filters)
        return [self._request_list(row) for row in rows], total

    def get_my_request(self, user: AuthUser, request_id: int) -> RentalRequestDetailOut:
        row = self.repo.get_request(request_id)
        if row is None or row.requester_user_id != user.id:
            raise ValidationAuthError(message="Rental request not found")
        return self._request_detail(row)

    def cancel_my_request(
        self, user: AuthUser, request_id: int, payload: RentalRequestCancelIn
    ) -> RentalRequestDetailOut:
        row = self.repo.get_request(request_id, lock=True)
        if row is None or row.requester_user_id != user.id:
            raise ValidationAuthError(message="Rental request not found")
        if row.status not in {
            RentalRequestStatus.PENDING.value,
            RentalRequestStatus.ACCEPTED.value,
        }:
            raise ValidationAuthError(
                message="Rental request cannot be cancelled in current status",
                details={"status": row.status},
            )
        row.cancel_reason = payload.reason
        old_status = row.status
        self._apply_request_status(
            row, RentalRequestStatus.CANCELLED.value, user.id, payload.reason
        )
        self._sync_financial_terms(row, RentalRequestStatus.CANCELLED.value)
        self._notify_request_transition(
            row,
            old_status=old_status,
            new_status=RentalRequestStatus.CANCELLED.value,
            actor_user_id=user.id,
            recipient_user_ids=[row.lessor_profile.user_id],
            lessor_action=False,
        )
        self.db.commit()
        return self._request_detail(self.repo.get_request(row.id))

    def list_assigned_requests(
        self, user: AuthUser, **filters
    ) -> tuple[list[RentalRequestListOut], int]:
        profile = self._approved_lessor(user)
        self._validate_request_status_filter(filters.get("status"))
        rows, total = self.repo.list_requests(lessor_profile_id=profile.id, **filters)
        return [self._request_list(row) for row in rows], total

    def get_assigned_request(self, user: AuthUser, request_id: int) -> RentalRequestDetailOut:
        profile = self._approved_lessor(user)
        row = self.repo.get_request(request_id)
        if row is None or row.lessor_profile_id != profile.id:
            raise ValidationAuthError(message="Rental request not found")
        return self._request_detail(row)

    def update_assigned_request(
        self, user: AuthUser, request_id: int, payload: RentalRequestStatusIn
    ) -> RentalRequestDetailOut:
        profile = self._approved_lessor(user)
        row = self.repo.get_request(request_id, lock=True)
        if row is None or row.lessor_profile_id != profile.id:
            raise ValidationAuthError(message="Rental request not found")
        if payload.status not in self.LESSOR_REQUEST_TRANSITIONS.get(row.status, set()):
            raise ValidationAuthError(
                message="Invalid lessor rental request transition",
                details={"from_status": row.status, "to_status": payload.status},
            )
        row.lessor_note = payload.note
        old_status = row.status
        if payload.status == RentalRequestStatus.ACCEPTED.value:
            self._accept_request(row)
        elif payload.status == RentalRequestStatus.IN_PROGRESS.value:
            self._require_financial_terms(row)
        self._apply_request_status(row, payload.status, user.id, payload.note)
        self._sync_financial_terms(row, payload.status)
        self._notify_request_transition(
            row,
            old_status=old_status,
            new_status=payload.status,
            actor_user_id=user.id,
            recipient_user_ids=[row.requester_user_id],
            lessor_action=True,
        )
        self.db.commit()
        return self._request_detail(self.repo.get_request(row.id))

    def list_admin_requests(self, **filters) -> tuple[list[RentalRequestListOut], int]:
        self._validate_request_status_filter(filters.get("status"))
        rows, total = self.repo.list_requests(**filters)
        return [self._request_list(row) for row in rows], total

    def get_admin_request(self, request_id: int) -> RentalRequestAdminDetailOut:
        row = self.repo.get_request(request_id)
        if row is None:
            raise ValidationAuthError(message="Rental request not found")
        return self._request_admin_detail(row)

    def update_admin_request(
        self, admin_user: AuthUser, request_id: int, payload: RentalRequestStatusIn
    ) -> RentalRequestAdminDetailOut:
        row = self.repo.get_request(request_id, lock=True)
        if row is None:
            raise ValidationAuthError(message="Rental request not found")
        if payload.status not in self.ADMIN_REQUEST_TRANSITIONS.get(row.status, set()):
            raise ValidationAuthError(
                message="Invalid Admin rental request transition",
                details={"from_status": row.status, "to_status": payload.status},
            )
        row.admin_note = payload.note
        old_status = row.status
        if payload.status == RentalRequestStatus.ACCEPTED.value:
            self._accept_request(row)
        elif payload.status == RentalRequestStatus.IN_PROGRESS.value:
            self._require_financial_terms(row)
        if payload.status == RentalRequestStatus.CANCELLED.value:
            row.cancel_reason = payload.note
        self._apply_request_status(row, payload.status, admin_user.id, payload.note)
        self._sync_financial_terms(row, payload.status)
        self._notify_request_transition(
            row,
            old_status=old_status,
            new_status=payload.status,
            actor_user_id=admin_user.id,
            recipient_user_ids=[row.requester_user_id],
            lessor_action=True,
        )
        self._notify_request_transition(
            row,
            old_status=old_status,
            new_status=payload.status,
            actor_user_id=admin_user.id,
            recipient_user_ids=[row.lessor_profile.user_id],
            lessor_action=False,
        )
        self.db.commit()
        return self._request_admin_detail(self.repo.get_request(row.id))

    def _accept_request(self, row: RentalRequest) -> None:
        equipment = self.repo.lock_equipment(row.equipment_id)
        pricing = self.repo.get_pricing_rule(row.pricing_rule_id)
        if (
            equipment is None
            or equipment.status != RentalEquipmentStatus.APPROVED.value
            or not equipment.is_active
        ):
            raise ValidationAuthError(message="Rental equipment is no longer available")
        if pricing is None or pricing.equipment_id != equipment.id or not pricing.is_active:
            raise ValidationAuthError(message="Rental pricing is no longer active")
        if row.requested_units < pricing.minimum_units:
            raise ValidationAuthError(message="Rental pricing minimum has changed")
        if row.operator_requested != pricing.operator_included:
            raise ValidationAuthError(message="Rental pricing operator mode has changed")
        if self.repo.list_availability_blocks(
            equipment.id, starts_at=row.starts_at, ends_at=row.ends_at
        ) or self.repo.conflicting_booking(
            equipment.id, row.starts_at, row.ends_at, exclude_request_id=row.id
        ):
            raise ValidationAuthError(message="Rental equipment has a conflicting block or booking")
        rental_amount = pricing.price_amount * row.requested_units
        deposit = equipment.security_deposit_amount or Decimal("0")
        row.price_per_unit_snapshot = pricing.price_amount
        row.rental_amount_snapshot = rental_amount
        row.deposit_amount_snapshot = deposit
        row.total_amount_snapshot = rental_amount + deposit
        row.currency = pricing.currency

    def _apply_request_status(
        self, row: RentalRequest, to_status: str, actor_id: int, note: str | None
    ) -> None:
        from_status = row.status
        row.status = to_status
        now = self._now()
        if to_status == RentalRequestStatus.ACCEPTED.value:
            row.accepted_at = now
        elif to_status == RentalRequestStatus.COMPLETED.value:
            row.completed_at = now
        elif to_status == RentalRequestStatus.CANCELLED.value:
            row.cancelled_at = now
        self.db.add(
            RentalRequestStatusLog(
                request_id=row.id,
                changed_by=actor_id,
                from_status=from_status,
                to_status=to_status,
                note=note,
                event_key=f"rental_request:{row.id}:status:{from_status}:{to_status}",
            )
        )

    def _require_financial_terms(self, row: RentalRequest) -> None:
        try:
            RentalFinancialService(self.db).require(rental_request_id=row.id)
        except RentalFinancialContractError as exc:
            raise ValidationAuthError(message=str(exc)) from exc

    def _sync_financial_terms(self, row: RentalRequest, status: str) -> None:
        finance = RentalFinancialService(self.db)
        try:
            if status == RentalRequestStatus.ACCEPTED.value:
                finance.snapshot(
                    request=row,
                    provider_user_id=row.lessor_profile.user_id,
                )
            elif status == RentalRequestStatus.CANCELLED.value:
                finance.cancel_unfunded(
                    rental_request_id=row.id,
                    at=row.cancelled_at or self._now(),
                )
            elif status == RentalRequestStatus.COMPLETED.value:
                finance.mark_operationally_completed_unfunded(
                    rental_request_id=row.id,
                    at=row.completed_at or self._now(),
                )
        except RentalFinancialContractError as exc:
            raise ValidationAuthError(message=str(exc)) from exc

    def _validate_request_status_filter(self, status: str | None) -> None:
        if status and status not in {item.value for item in RentalRequestStatus}:
            raise ValidationAuthError(
                message="Invalid rental request status", details={"status": status}
            )

    @staticmethod
    def _request_notification_payload(
        row: RentalRequest, *, old_status: str | None, new_status: str
    ) -> dict:
        return {
            "request_id": row.id,
            "equipment_id": row.equipment_id,
            "lessor_profile_id": row.lessor_profile_id,
            "requester_user_id": row.requester_user_id,
            "old_status": old_status,
            "new_status": new_status,
        }

    def _notify_request_created(self, row: RentalRequest, *, actor_user_id: int) -> None:
        NotificationService(self.db).create_event_and_notify_user(
            event_type=NotificationEventType.RENTAL_REQUEST_CREATED.value,
            event_key=f"rental_request:{row.id}:created",
            recipient_user_id=row.lessor_profile.user_id,
            title="درخواست اجاره جدید",
            body=f"یک درخواست جدید برای اجاره «{row.equipment.title}» ثبت شد.",
            actor_user_id=actor_user_id,
            source_type="rental_request",
            source_id=str(row.id),
            payload_json=self._request_notification_payload(
                row, old_status=None, new_status=RentalRequestStatus.PENDING.value
            ),
            action_url=f"/rentals/requests/assigned/{row.id}",
            priority=NotificationPriority.NORMAL.value,
            commit=False,
        )

    def _notify_request_transition(
        self,
        row: RentalRequest,
        *,
        old_status: str,
        new_status: str,
        actor_user_id: int,
        recipient_user_ids: list[int],
        lessor_action: bool,
    ) -> None:
        event_by_status = {
            RentalRequestStatus.ACCEPTED.value: NotificationEventType.RENTAL_REQUEST_ACCEPTED,
            RentalRequestStatus.REJECTED.value: NotificationEventType.RENTAL_REQUEST_REJECTED,
            RentalRequestStatus.IN_PROGRESS.value: NotificationEventType.RENTAL_REQUEST_IN_PROGRESS,
            RentalRequestStatus.COMPLETED.value: NotificationEventType.RENTAL_REQUEST_COMPLETED,
            RentalRequestStatus.CANCELLED.value: NotificationEventType.RENTAL_REQUEST_CANCELLED,
        }
        event_type = event_by_status.get(new_status)
        recipients = sorted({user_id for user_id in recipient_user_ids if user_id != actor_user_id})
        if event_type is None or not recipients:
            return
        NotificationService(self.db).create_event_and_notify_many(
            event_type=event_type.value,
            event_key=f"rental_request:{row.id}:{old_status}:{new_status}",
            recipient_user_ids=recipients,
            title="وضعیت درخواست اجاره تغییر کرد",
            body=f"درخواست اجاره «{row.equipment.title}» به وضعیت {new_status} تغییر کرد.",
            actor_user_id=actor_user_id,
            source_type="rental_request",
            source_id=str(row.id),
            payload_json=self._request_notification_payload(
                row, old_status=old_status, new_status=new_status
            ),
            action_url=(
                f"/rentals/requests/{row.id}"
                if lessor_action
                else f"/rentals/requests/assigned/{row.id}"
            ),
            priority=NotificationPriority.NORMAL.value,
            commit=False,
        )

    def _request_list(self, row: RentalRequest) -> RentalRequestListOut:
        fields = (
            "id",
            "requester_user_id",
            "lessor_profile_id",
            "equipment_id",
            "pricing_rule_id",
            "starts_at",
            "ends_at",
            "requested_units",
            "operator_requested",
            "status",
            "price_per_unit_snapshot",
            "rental_amount_snapshot",
            "deposit_amount_snapshot",
            "total_amount_snapshot",
            "currency",
            "created_at",
            "updated_at",
        )
        return RentalRequestListOut(
            **{field: getattr(row, field) for field in fields},
            equipment_title=row.equipment.title if row.equipment else "",
            lessor_display_name=row.lessor_profile.display_name if row.lessor_profile else None,
        )

    def _request_detail(self, row: RentalRequest) -> RentalRequestDetailOut:
        return RentalRequestDetailOut(
            **self._request_list(row).model_dump(),
            delivery_address=row.delivery_address,
            requester_note=row.requester_note,
            lessor_note=row.lessor_note,
            cancel_reason=row.cancel_reason,
            accepted_at=row.accepted_at,
            completed_at=row.completed_at,
            cancelled_at=row.cancelled_at,
            status_logs=[
                self._status_log_out(log)
                for log in sorted(row.status_logs, key=lambda item: (item.created_at, item.id))
            ],
        )

    def _request_admin_detail(self, row: RentalRequest) -> RentalRequestAdminDetailOut:
        return RentalRequestAdminDetailOut(
            **self._request_detail(row).model_dump(), admin_note=row.admin_note
        )

    @staticmethod
    def _status_log_out(row: RentalRequestStatusLog) -> RentalRequestStatusLogOut:
        return RentalRequestStatusLogOut(
            id=row.id,
            changed_by=row.changed_by,
            from_status=row.from_status,
            to_status=row.to_status,
            note=row.note,
            created_at=row.created_at,
        )

    def _pricing_row(self, payload: RentalPricingRuleIn, operator_mode: str) -> RentalPricingRule:
        if payload.unit not in {item.value for item in RentalPricingUnit}:
            raise ValidationAuthError(
                message="Invalid rental pricing unit", details={"unit": payload.unit}
            )
        if (
            operator_mode == RentalOperatorMode.WITH_OPERATOR.value
            and not payload.operator_included
        ):
            raise ValidationAuthError(message="Pricing must include operator for this equipment")
        if operator_mode == RentalOperatorMode.WITHOUT_OPERATOR.value and payload.operator_included:
            raise ValidationAuthError(message="Pricing cannot include operator for this equipment")
        return RentalPricingRule(
            unit=payload.unit,
            operator_included=payload.operator_included,
            price_amount=payload.price_amount,
            minimum_units=payload.minimum_units,
            currency=payload.currency.upper(),
            is_active=payload.is_active,
        )

    def _pricing_out(self, row: RentalPricingRule) -> RentalPricingRuleOut:
        fields = (
            "id",
            "equipment_id",
            "unit",
            "operator_included",
            "price_amount",
            "minimum_units",
            "currency",
            "is_active",
            "created_at",
            "updated_at",
        )
        return RentalPricingRuleOut(**{field: getattr(row, field) for field in fields})

    def _block_out(
        self, row: RentalAvailabilityBlock, *, include_note: bool = True
    ) -> RentalAvailabilityBlockOut:
        return RentalAvailabilityBlockOut(
            id=row.id,
            equipment_id=row.equipment_id,
            block_type=row.block_type,
            starts_at=row.starts_at,
            ends_at=row.ends_at,
            note=row.note if include_note else None,
            created_at=row.created_at,
        )

    def _valid_range(self, starts_at: datetime, ends_at: datetime) -> tuple[datetime, datetime]:
        starts_at = self._naive_utc(starts_at)
        ends_at = self._naive_utc(ends_at)
        if ends_at <= starts_at:
            raise ValidationAuthError(message="Rental availability end must be after start")
        return starts_at, ends_at

    @staticmethod
    def _naive_utc(value: datetime) -> datetime:
        return value.astimezone(timezone.utc).replace(tzinfo=None) if value.tzinfo else value

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _validate_block_type(value: str) -> None:
        if value not in {item.value for item in RentalAvailabilityBlockType}:
            raise ValidationAuthError(
                message="Invalid rental availability block type", details={"block_type": value}
            )

    def _validate_equipment_filters(self, filters: dict) -> None:
        mode = filters.get("operator_mode")
        if mode and mode not in {item.value for item in RentalOperatorMode}:
            raise ValidationAuthError(
                message="Invalid rental operator mode", details={"operator_mode": mode}
            )
        status = filters.get("status")
        if status and status not in {item.value for item in RentalEquipmentStatus}:
            raise ValidationAuthError(
                message="Invalid rental equipment status", details={"status": status}
            )
        sort = filters.get("sort")
        if sort and sort not in {item.value for item in RentalDiscoverySort}:
            raise ValidationAuthError(
                message="Invalid rental discovery sort", details={"sort": sort}
            )
        min_price, max_price = filters.get("min_price"), filters.get("max_price")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationAuthError(message="min_price must be less than or equal to max_price")
        available_from = filters.get("available_from")
        available_to = filters.get("available_to")
        if (available_from is None) != (available_to is None):
            raise ValidationAuthError(
                message="Rental availability range requires both start and end"
            )
        if available_from is not None and available_to is not None:
            filters["available_from"], filters["available_to"] = self._valid_range(
                available_from, available_to
            )

    def _equipment_out(self, row: RentalEquipment) -> RentalEquipmentOut:
        media = []
        for item in sorted(row.media or [], key=lambda value: (value.sort_order, value.id)):
            file = self.repo.get_media(item.media_file_id)
            key = file.file_key if file else None
            media.append(
                RentalEquipmentMediaOut(
                    id=item.id,
                    media_file_id=item.media_file_id,
                    file_key=key,
                    public_url=f"/api/v1/media/public/{key}" if key else None,
                    sort_order=item.sort_order,
                    is_primary=item.is_primary,
                    alt_text=item.alt_text,
                )
            )
        category = self._category_out(row.category) if row.category else None
        fields = (
            "id",
            "lessor_profile_id",
            "category_id",
            "title",
            "slug",
            "description",
            "manufacturer",
            "model_name",
            "production_year",
            "operator_mode",
            "status",
            "province_id",
            "city_id",
            "address_text",
            "delivery_available",
            "delivery_terms",
            "security_deposit_amount",
            "currency",
            "is_active",
            "admin_note",
            "submitted_at",
            "approved_at",
            "approved_by",
            "created_at",
            "updated_at",
        )
        return RentalEquipmentOut(
            **{field: getattr(row, field) for field in fields},
            media=media,
            category=category,
            lessor_display_name=row.lessor_profile.display_name if row.lessor_profile else None,
        )

    def _public_equipment_out(self, row: RentalEquipment) -> RentalEquipmentPublicOut:
        owner = self._equipment_out(row)
        return RentalEquipmentPublicOut(
            **owner.model_dump(
                exclude={
                    "status",
                    "address_text",
                    "is_active",
                    "admin_note",
                    "submitted_at",
                    "approved_at",
                    "approved_by",
                    "created_at",
                    "updated_at",
                }
            )
        )

    def _validate_parent(self, category_id: int, parent_id: int | None) -> None:
        if parent_id is None:
            return
        if parent_id == category_id:
            raise ValidationAuthError(message="Rental category cannot be its own parent")
        current = self._require_category(parent_id)
        seen = {category_id}
        while current.parent_id is not None:
            if current.parent_id in seen:
                raise ValidationAuthError(message="Rental category hierarchy cycle detected")
            seen.add(current.id)
            current = self._require_category(current.parent_id)

    def _require_category(self, category_id: int) -> RentalCategory:
        row = self.repo.get_category(category_id)
        if row is None:
            raise ValidationAuthError(
                message="Rental category not found", details={"category_id": category_id}
            )
        return row

    def _commit_unique(self, message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ValidationAuthError(message=message) from exc

    def _category_out(self, row: RentalCategory) -> RentalCategoryOut:
        children, equipment = self.repo.category_counts(row.id)
        return RentalCategoryOut(
            **{
                column: getattr(row, column)
                for column in (
                    "id",
                    "parent_id",
                    "code",
                    "title",
                    "description",
                    "sort_order",
                    "is_active",
                    "created_at",
                    "updated_at",
                )
            },
            children_count=children,
            equipment_count=equipment,
        )

    def _profile_out(self, row: LessorProfile) -> LessorProfileOut:
        fields = (
            "id",
            "user_id",
            "display_name",
            "bio",
            "phone",
            "province_id",
            "city_id",
            "address_text",
            "avatar_media_file_id",
            "status",
            "admin_note",
            "submitted_at",
            "approved_at",
            "approved_by",
            "created_at",
            "updated_at",
        )
        return LessorProfileOut(
            **{field: getattr(row, field) for field in fields},
            equipment_count=self.repo.equipment_count(row.id),
        )
