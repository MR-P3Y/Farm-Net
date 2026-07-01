from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository
from app.modules.media.enums import MediaStatus, MediaVisibility
from app.modules.notifications.enums import NotificationEventType, NotificationPriority
from app.modules.notifications.service import NotificationService
from app.modules.services.enums import ServiceProviderStatus
from app.modules.services.models import ServiceCategory, ServiceProviderProfile
from app.modules.services.repository import ServicesRepository
from app.modules.services.schemas import (
    ServiceCategoryCreateIn,
    ServiceCategoryOut,
    ServiceCategoryUpdateIn,
    ServiceProviderProfileCreateIn,
    ServiceProviderProfileOut,
    ServiceProviderProfilePublicOut,
    ServiceProviderProfileStatusUpdateIn,
    ServiceProviderProfileUpdateIn,
)


class ServicesService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ServicesRepository(db)
        self.auth_repo = AuthRepository(db)

    def seed_default_categories(self) -> list[ServiceCategoryOut]:
        defaults = [
            {
                "code": "spraying",
                "title": "سم‌پاشی",
                "description": "خدمات سم‌پاشی مزارع، باغ‌ها و گلخانه‌ها",
                "sort_order": 100,
            },
            {
                "code": "plowing",
                "title": "شخم‌زنی",
                "description": "آماده‌سازی و شخم زمین کشاورزی",
                "sort_order": 200,
            },
            {
                "code": "pruning",
                "title": "هرس",
                "description": "خدمات هرس درختان و باغ‌ها",
                "sort_order": 300,
            },
            {
                "code": "harvesting",
                "title": "برداشت",
                "description": "خدمات برداشت محصول",
                "sort_order": 400,
            },
            {
                "code": "crop_transport",
                "title": "حمل محصول",
                "description": "حمل و جابه‌جایی محصولات کشاورزی",
                "sort_order": 500,
            },
            {
                "code": "soil_testing",
                "title": "آزمایش خاک",
                "description": "نمونه‌برداری و خدمات آزمایش خاک",
                "sort_order": 600,
            },
            {
                "code": "irrigation_installation",
                "title": "نصب آبیاری",
                "description": "نصب و راه‌اندازی سیستم‌های آبیاری",
                "sort_order": 700,
            },
            {
                "code": "labor",
                "title": "نیروی کارگری",
                "description": "تأمین نیروی کار برای عملیات کشاورزی",
                "sort_order": 800,
            },
        ]

        rows: list[ServiceCategory] = []

        for item in defaults:
            row = self.repo.get_category_by_code(item["code"])
            if row is None:
                row = ServiceCategory(
                    code=item["code"],
                    title=item["title"],
                    description=item["description"],
                    sort_order=item["sort_order"],
                    is_active=True,
                )
                self.repo.add_category(row)
            else:
                row.title = item["title"]
                row.description = item["description"]
                row.sort_order = item["sort_order"]
                row.is_active = True
            rows.append(row)

        self.repo.commit()

        for row in rows:
            self.repo.refresh(row)

        return [ServiceCategoryOut.model_validate(row) for row in rows]

    def list_categories(
        self,
        *,
        active_only: bool = True,
        q: str | None = None,
    ) -> list[ServiceCategoryOut]:
        return [
            ServiceCategoryOut.model_validate(row)
            for row in self.repo.list_categories(active_only=active_only, q=q)
        ]

    def create_category(self, payload: ServiceCategoryCreateIn) -> ServiceCategoryOut:
        code = self._normalize_code(payload.code)
        self._validate_parent_category(payload.parent_id)

        row = ServiceCategory(
            parent_id=payload.parent_id,
            code=code,
            title=payload.title.strip(),
            description=payload.description,
            sort_order=payload.sort_order,
            is_active=payload.is_active,
        )
        self.repo.add_category(row)

        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(
                message="Service category code already exists",
                details={"code": code},
            ) from exc

        self.repo.refresh(row)
        return ServiceCategoryOut.model_validate(row)

    def update_category(
        self,
        *,
        category_id: int,
        payload: ServiceCategoryUpdateIn,
    ) -> ServiceCategoryOut:
        row = self.repo.get_category_by_id(category_id)

        if row is None:
            raise ValidationAuthError(
                message="Service category not found",
                details={"category_id": category_id},
            )

        if payload.parent_id is not None:
            if payload.parent_id == row.id:
                raise ValidationAuthError(message="Service category cannot be its own parent")
            self._validate_parent_category(payload.parent_id)
            row.parent_id = payload.parent_id
        if payload.code is not None:
            row.code = self._normalize_code(payload.code)
        if payload.title is not None:
            row.title = payload.title.strip()
        if payload.description is not None:
            row.description = payload.description
        if payload.sort_order is not None:
            row.sort_order = payload.sort_order
        if payload.is_active is not None:
            row.is_active = payload.is_active

        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(
                message="Service category code already exists",
                details={"code": row.code},
            ) from exc

        self.repo.refresh(row)
        return ServiceCategoryOut.model_validate(row)

    def get_my_provider_profile(self, user: AuthUser) -> ServiceProviderProfileOut | None:
        profile = self.repo.get_profile_by_user_id(user.id)
        return self._profile_out(profile) if profile else None

    def create_or_update_my_provider_profile(
        self,
        *,
        user: AuthUser,
        payload: ServiceProviderProfileCreateIn | ServiceProviderProfileUpdateIn,
    ) -> ServiceProviderProfileOut:
        self._validate_category_ids(payload.category_ids, require_active=True)
        self._validate_avatar_media(
            media_file_id=payload.avatar_media_file_id,
            owner_user_id=user.id,
        )

        profile = self.repo.get_profile_by_user_id(user.id)
        if profile is None:
            profile = ServiceProviderProfile(
                user_id=user.id,
                status=ServiceProviderStatus.DRAFT.value,
            )
            self.repo.add_profile(profile)

        if profile.status == ServiceProviderStatus.SUSPENDED.value:
            raise ValidationAuthError(
                message="Suspended service provider profile cannot be updated",
                details={"profile_id": profile.id},
            )

        profile.display_name = payload.display_name
        profile.title = payload.title
        profile.bio = payload.bio
        profile.experience_years = payload.experience_years
        profile.phone = payload.phone
        profile.email = payload.email
        profile.province_id = payload.province_id
        profile.city_id = payload.city_id
        profile.village_id = payload.village_id
        profile.province_name = payload.province_name
        profile.city_name = payload.city_name
        profile.village_name = payload.village_name
        profile.service_area = payload.service_area
        profile.avatar_file_id = payload.avatar_file_id
        profile.avatar_media_file_id = payload.avatar_media_file_id

        self.repo.replace_profile_categories(
            profile=profile,
            category_ids=self._unique_ids(payload.category_ids),
        )

        self.repo.commit()
        self.repo.refresh(profile)
        return self._profile_out(profile)

    def submit_my_provider_profile(self, user: AuthUser) -> ServiceProviderProfileOut:
        profile = self.repo.get_profile_by_user_id(user.id)

        if profile is None:
            raise ValidationAuthError(message="Service provider profile not found")

        if profile.status not in {
            ServiceProviderStatus.DRAFT.value,
            ServiceProviderStatus.REJECTED.value,
        }:
            raise ValidationAuthError(
                message="Service provider profile cannot be submitted in current status",
                details={"current_status": profile.status},
            )

        missing = []
        if not self._resolved_display_name(profile):
            missing.append("display_name")
        if not profile.title:
            missing.append("title")
        if not profile.bio:
            missing.append("bio")
        if not profile.service_area:
            missing.append("service_area")
        if not profile.category_links:
            missing.append("category_ids")

        if missing:
            raise ValidationAuthError(
                message="Service provider profile is not ready for review",
                details={"missing": missing},
            )

        profile.status = ServiceProviderStatus.PENDING_REVIEW.value
        profile.submitted_at = datetime.utcnow()
        profile.admin_note = None

        self.repo.commit()
        self.repo.refresh(profile)
        self._notify_profile_submitted(profile)

        return self._profile_out(profile)

    def list_admin_provider_profiles(
        self,
        *,
        status: str | None,
        category_id: int | None,
        q: str | None,
        province_id: int | None,
        city_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ServiceProviderProfileOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_profile_status(status)

        if category_id is not None:
            category = self.repo.get_category_by_id(category_id)
            if category is None:
                raise ValidationAuthError(
                    message="Service category not found",
                    details={"category_id": category_id},
                )

        rows, total = self.repo.list_profiles(
            status=status,
            category_id=category_id,
            q=q,
            province_id=province_id,
            city_id=city_id,
            page=page,
            page_size=page_size,
        )

        return [self._profile_out(row) for row in rows], total

    def get_admin_provider_profile(self, profile_id: int) -> ServiceProviderProfileOut:
        profile = self.repo.get_profile_by_id(profile_id)

        if profile is None or profile.deleted_at is not None:
            raise ValidationAuthError(
                message="Service provider profile not found",
                details={"profile_id": profile_id},
            )

        return self._profile_out(profile)

    def update_provider_profile_status_admin(
        self,
        *,
        profile_id: int,
        admin_user: AuthUser,
        payload: ServiceProviderProfileStatusUpdateIn,
    ) -> ServiceProviderProfileOut:
        status = self._validate_profile_status(payload.status)
        profile = self.repo.get_profile_by_id(profile_id)

        if profile is None or profile.deleted_at is not None:
            raise ValidationAuthError(
                message="Service provider profile not found",
                details={"profile_id": profile_id},
            )

        now = datetime.utcnow()
        profile.status = status
        profile.admin_note = payload.note

        if status == ServiceProviderStatus.APPROVED.value:
            profile.approved_at = now
            profile.approved_by = admin_user.id
            profile.rejected_at = None
            profile.rejected_by = None
            profile.suspended_at = None
            profile.suspended_by = None
            self._assign_service_provider_role(profile.user_id, assigned_by=admin_user.id)
        elif status == ServiceProviderStatus.REJECTED.value:
            profile.rejected_at = now
            profile.rejected_by = admin_user.id
        elif status == ServiceProviderStatus.SUSPENDED.value:
            profile.suspended_at = now
            profile.suspended_by = admin_user.id

        self.repo.commit()
        self.repo.refresh(profile)
        self._notify_profile_status(profile, status)

        return self._profile_out(profile)

    def _profile_out(self, profile: ServiceProviderProfile) -> ServiceProviderProfileOut:
        display_name = self._resolved_display_name(profile)
        avatar_file_id = profile.avatar_file_id

        user_profile = self.repo.get_user_profile(profile.user_id)
        if user_profile is not None:
            avatar_file_id = avatar_file_id or user_profile.avatar_file_id

        avatar_url = None
        if profile.avatar_media_file_id:
            media = self.repo.get_media_file_by_id(profile.avatar_media_file_id)
            if media is not None and media.file_key:
                avatar_url = f"/api/v1/media/public/{media.file_key}"

        categories = [
            ServiceCategoryOut.model_validate(link.category)
            for link in profile.category_links
            if link.category is not None
        ]

        return ServiceProviderProfileOut(
            id=profile.id,
            user_id=profile.user_id,
            display_name=display_name,
            name=display_name,
            title=profile.title,
            bio=profile.bio or (user_profile.bio if user_profile else None),
            experience_years=profile.experience_years,
            phone=profile.phone,
            email=profile.email,
            province_id=profile.province_id,
            city_id=profile.city_id,
            village_id=profile.village_id,
            province_name=profile.province_name,
            city_name=profile.city_name,
            village_name=profile.village_name,
            service_area=profile.service_area,
            avatar_file_id=avatar_file_id,
            avatar_media_file_id=profile.avatar_media_file_id,
            avatar_url=avatar_url,
            status=profile.status,
            is_verified=profile.status == ServiceProviderStatus.APPROVED.value,
            verification_status=profile.status,
            is_featured=profile.is_featured,
            rating_average=profile.rating_average or Decimal("0.00"),
            reviews_count=profile.reviews_count,
            requests_count=profile.requests_count,
            completed_requests_count=profile.completed_requests_count,
            categories=categories,
            admin_note=profile.admin_note,
            submitted_at=profile.submitted_at,
            approved_at=profile.approved_at,
            approved_by=profile.approved_by,
            rejected_at=profile.rejected_at,
            rejected_by=profile.rejected_by,
            suspended_at=profile.suspended_at,
            suspended_by=profile.suspended_by,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    def _public_profile_out(
        self,
        profile: ServiceProviderProfile,
    ) -> ServiceProviderProfilePublicOut:
        return ServiceProviderProfilePublicOut.model_validate(
            self._profile_out(profile).model_dump()
        )

    def _resolved_display_name(self, profile: ServiceProviderProfile) -> str | None:
        if profile.display_name:
            return profile.display_name

        user_profile = self.repo.get_user_profile(profile.user_id)
        if user_profile is None:
            return None

        if user_profile.display_name:
            return user_profile.display_name

        parts = [user_profile.first_name, user_profile.last_name]
        name = " ".join([part for part in parts if part])
        return name or None

    def _validate_parent_category(self, parent_id: int | None) -> None:
        if parent_id is None:
            return

        parent = self.repo.get_category_by_id(parent_id)
        if parent is None:
            raise ValidationAuthError(
                message="Parent service category not found",
                details={"parent_id": parent_id},
            )

    def _validate_category_ids(
        self,
        category_ids: list[int],
        *,
        require_active: bool,
    ) -> None:
        unique_ids = self._unique_ids(category_ids)
        if len(unique_ids) != len(category_ids):
            raise ValidationAuthError(message="Duplicate category_ids are not allowed")

        for category_id in unique_ids:
            category = self.repo.get_category_by_id(category_id)
            if category is None or (require_active and not category.is_active):
                raise ValidationAuthError(
                    message="Service category not found",
                    details={"category_id": category_id},
                )

    def _validate_avatar_media(
        self,
        *,
        media_file_id: int | None,
        owner_user_id: int,
    ) -> None:
        if media_file_id is None:
            return

        media = self.repo.get_media_file_by_id(media_file_id)
        if media is None or media.owner_user_id != owner_user_id:
            raise ValidationAuthError(
                message="Avatar media file not found",
                details={"avatar_media_file_id": media_file_id},
            )

        if media.status != MediaStatus.ACTIVE.value:
            raise ValidationAuthError(
                message="Avatar media file is not active",
                details={"avatar_media_file_id": media_file_id},
            )

        if media.visibility != MediaVisibility.PUBLIC.value:
            raise ValidationAuthError(
                message="Service provider avatar must be public",
                details={"avatar_media_file_id": media_file_id},
            )

    def _normalize_code(self, code: str) -> str:
        clean = code.strip().lower().replace(" ", "_")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,98}[a-z0-9]", clean):
            raise ValidationAuthError(
                message="Invalid service category code",
                details={"format": "lowercase letters, numbers, underscore or dash"},
            )
        return clean

    def _validate_profile_status(self, status: str) -> str:
        allowed = {item.value for item in ServiceProviderStatus}
        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid service provider profile status",
                details={"allowed": sorted(allowed)},
            )
        return status

    def _assign_service_provider_role(self, user_id: int, *, assigned_by: int) -> None:
        role = self.auth_repo.get_role_by_code("service_provider")
        if role is None:
            return
        self.auth_repo.assign_role_to_user(
            user_id=user_id,
            role_id=role.id,
            assigned_by=assigned_by,
        )

    def _notify_profile_submitted(self, profile: ServiceProviderProfile) -> None:
        admin_ids = self.repo.list_service_admin_recipient_user_ids()
        if not admin_ids:
            return

        NotificationService(self.db).create_event_and_notify_many(
            event_type=NotificationEventType.SERVICE_PROVIDER_SUBMITTED.value,
            recipient_user_ids=admin_ids,
            title="درخواست ارائه‌دهنده خدمات جدید",
            body=f"کاربر #{profile.user_id} پروفایل ارائه‌دهنده خدمات خود را برای بررسی ارسال کرد.",
            actor_user_id=profile.user_id,
            source_type="service_provider_profile",
            source_id=str(profile.id),
            payload_json={"profile_id": profile.id, "user_id": profile.user_id},
            action_url=f"/admin/services/provider-profiles?profile_id={profile.id}",
            priority=NotificationPriority.HIGH.value,
            commit=True,
        )

    def _notify_profile_status(self, profile: ServiceProviderProfile, status: str) -> None:
        if status == ServiceProviderStatus.APPROVED.value:
            event_type = NotificationEventType.SERVICE_PROVIDER_APPROVED.value
            title = "پروفایل ارائه‌دهنده خدمات شما تأیید شد"
            body = "پروفایل خدمات شما فعال شد و می‌توانید خدمات خود را مدیریت کنید."
        elif status == ServiceProviderStatus.REJECTED.value:
            event_type = NotificationEventType.SERVICE_PROVIDER_REJECTED.value
            title = "پروفایل ارائه‌دهنده خدمات شما رد شد"
            body = profile.admin_note or "پروفایل خدمات شما نیاز به اصلاح دارد."
        else:
            return

        NotificationService(self.db).create_event_and_notify_user(
            event_type=event_type,
            recipient_user_id=profile.user_id,
            title=title,
            body=body,
            actor_user_id=profile.approved_by or profile.rejected_by or profile.suspended_by,
            source_type="service_provider_profile",
            source_id=str(profile.id),
            payload_json={"profile_id": profile.id, "status": status},
            action_url="/services/me/provider-profile",
            priority=NotificationPriority.HIGH.value,
            commit=True,
        )

    def _unique_ids(self, values: list[int]) -> list[int]:
        return list(dict.fromkeys(values))
