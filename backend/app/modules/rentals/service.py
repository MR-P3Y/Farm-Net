from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.profiles.enums import VerificationStatus, VerificationTargetRole
from app.modules.profiles.models import VerificationRequest
from app.modules.rentals.enums import LessorStatus
from app.modules.rentals.models import LessorProfile, RentalCategory
from app.modules.rentals.repository import RentalRepository
from app.modules.rentals.schemas import (
    RentalCategoryCreateIn,
    RentalCategoryOut,
    RentalCategoryUpdateIn,
    LessorProfileInput,
    LessorProfileOut,
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
