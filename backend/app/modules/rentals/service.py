import re
from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.media.enums import MediaStatus, MediaVisibility
from app.modules.profiles.enums import VerificationStatus, VerificationTargetRole
from app.modules.profiles.models import VerificationRequest
from app.modules.rentals.enums import LessorStatus, RentalEquipmentStatus, RentalOperatorMode
from app.modules.rentals.models import (
    LessorProfile,
    RentalCategory,
    RentalEquipment,
    RentalEquipmentMedia,
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
)


class RentalService:
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
        row.submitted_at = datetime.utcnow()
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
            row.approved_at = datetime.utcnow()
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
        row.submitted_at = datetime.utcnow()
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
        if (
            status in {RentalEquipmentStatus.REJECTED.value, RentalEquipmentStatus.SUSPENDED.value}
            and not admin_note
        ):
            raise ValidationAuthError(message="Admin note is required for this status")
        row.status = status
        row.admin_note = admin_note
        if status == RentalEquipmentStatus.APPROVED.value:
            row.approved_at = datetime.utcnow()
            row.approved_by = admin_user.id
        self.db.commit()
        self.db.refresh(row)
        return self._equipment_out(self.repo.get_equipment(row.id))

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
