from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import PermissionDeniedError, ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository
from app.modules.media.enums import MediaStatus, MediaVisibility
from app.modules.notifications.enums import NotificationEventType, NotificationPriority
from app.modules.notifications.service import NotificationService
from app.modules.services.enums import (
    ServiceContactMethod,
    ServiceOfferStatus,
    ServicePricingType,
    ServiceProviderStatus,
    ServiceRequestStatus,
)
from app.modules.services.models import (
    ServiceCategory,
    ServiceOffer,
    ServiceOfferMedia,
    ServiceProviderProfile,
    ServiceRequest,
    ServiceRequestStatusLog,
)
from app.modules.services.repository import ServicesRepository
from app.modules.services.schemas import (
    ServiceCategoryCreateIn,
    ServiceCategoryOut,
    ServiceCategoryUpdateIn,
    ServiceOfferCreateIn,
    ServiceOfferMediaIn,
    ServiceOfferMediaOut,
    ServiceOfferOut,
    ServiceOfferPublicOut,
    ServiceOfferStatusUpdateIn,
    ServiceOfferUpdateIn,
    ServiceProviderProfileCreateIn,
    ServiceProviderProfileOut,
    ServiceProviderProfilePublicOut,
    ServiceProviderProfileStatusUpdateIn,
    ServiceProviderProfileUpdateIn,
    ServiceRequestCancelIn,
    ServiceRequestCreateIn,
    ServiceRequestDetailOut,
    ServiceRequestOut,
    ServiceRequestStatusLogOut,
    ServiceRequestStatusUpdateIn,
)


class ServicesService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ServicesRepository(db)
        self.auth_repo = AuthRepository(db)

    PROVIDER_REQUEST_TRANSITIONS = {
        ServiceRequestStatus.OPEN.value: {
            ServiceRequestStatus.ACCEPTED.value,
            ServiceRequestStatus.REJECTED.value,
        },
        ServiceRequestStatus.ACCEPTED.value: {ServiceRequestStatus.IN_PROGRESS.value},
        ServiceRequestStatus.IN_PROGRESS.value: {ServiceRequestStatus.COMPLETED.value},
    }
    ADMIN_REQUEST_TRANSITIONS = {
        ServiceRequestStatus.OPEN.value: {
            ServiceRequestStatus.ACCEPTED.value,
            ServiceRequestStatus.REJECTED.value,
            ServiceRequestStatus.CANCELLED.value,
        },
        ServiceRequestStatus.ACCEPTED.value: {
            ServiceRequestStatus.IN_PROGRESS.value,
            ServiceRequestStatus.CANCELLED.value,
        },
        ServiceRequestStatus.IN_PROGRESS.value: {
            ServiceRequestStatus.COMPLETED.value,
            ServiceRequestStatus.CANCELLED.value,
        },
    }

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

    def list_public_offers(
        self,
        *,
        category_id: int | None,
        provider_profile_id: int | None,
        pricing_type: str | None,
        q: str | None,
        province_id: int | None,
        city_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ServiceOfferPublicOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if category_id is not None:
            self._validate_offer_category(category_id, require_active=True)

        if pricing_type is not None:
            self._validate_pricing_type(pricing_type)

        rows, total = self.repo.list_public_offers(
            category_id=category_id,
            provider_profile_id=provider_profile_id,
            pricing_type=pricing_type,
            q=q,
            province_id=province_id,
            city_id=city_id,
            page=page,
            page_size=page_size,
        )

        return [self._public_offer_out(row) for row in rows], total

    def get_public_offer(self, offer_id: int) -> ServiceOfferPublicOut:
        row = self.repo.get_public_offer_by_id(offer_id)

        if row is None:
            raise ValidationAuthError(
                message="Service offer not found",
                details={"offer_id": offer_id},
            )

        row.views_count += 1
        self.repo.commit()
        self.repo.refresh(row)

        return self._public_offer_out(row)

    def list_my_offers(
        self,
        *,
        user: AuthUser,
        status: str | None,
        category_id: int | None,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ServiceOfferOut], int]:
        provider = self._get_approved_provider_profile(user)

        if status is not None:
            self._validate_offer_status(status)

        if category_id is not None:
            self._validate_offer_category(category_id, require_active=False)

        rows, total = self.repo.list_provider_offers(
            provider_profile_id=provider.id,
            status=status,
            category_id=category_id,
            q=q,
            page=max(page, 1),
            page_size=min(max(page_size, 1), 100),
        )

        return [self._offer_out(row) for row in rows], total

    def create_my_offer(
        self,
        *,
        user: AuthUser,
        payload: ServiceOfferCreateIn,
    ) -> ServiceOfferOut:
        provider = self._get_approved_provider_profile(user)
        pricing_type = self._validate_pricing_type(payload.pricing_type)
        self._validate_offer_price(pricing_type=pricing_type, price_amount=payload.price_amount)
        if payload.category_id is not None:
            self._validate_offer_category(payload.category_id, require_active=True)

        row = ServiceOffer(
            provider_profile_id=provider.id,
            category_id=payload.category_id,
            title=payload.title.strip(),
            slug=self._normalize_slug(payload.slug),
            short_description=payload.short_description,
            description=payload.description,
            status=ServiceOfferStatus.DRAFT.value,
            pricing_type=pricing_type,
            price_amount=payload.price_amount,
            currency=payload.currency.upper(),
            province_id=payload.province_id,
            city_id=payload.city_id,
            village_id=payload.village_id,
            province_name=payload.province_name,
            city_name=payload.city_name,
            village_name=payload.village_name,
            service_area=payload.service_area,
            latitude=payload.latitude,
            longitude=payload.longitude,
            is_active=payload.is_active,
            is_featured=False,
            views_count=0,
            requests_count=0,
            completed_requests_count=0,
        )

        self.repo.add_offer(row)
        self.repo.replace_offer_media(
            offer=row,
            rows=self._offer_media_rows(
                payload.media_items,
                owner_user_id=user.id,
            ),
        )

        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(
                message="Service offer slug already exists for this provider",
                details={"slug": row.slug},
            ) from exc

        self.repo.refresh(row)
        return self._offer_out(row)

    def update_my_offer(
        self,
        *,
        user: AuthUser,
        offer_id: int,
        payload: ServiceOfferUpdateIn,
    ) -> ServiceOfferOut:
        provider = self._get_approved_provider_profile(user)
        row = self._get_owned_offer(provider_profile_id=provider.id, offer_id=offer_id)

        if row.status in {
            ServiceOfferStatus.SUSPENDED.value,
            ServiceOfferStatus.ARCHIVED.value,
        }:
            raise ValidationAuthError(
                message="Service offer cannot be updated in current status",
                details={"current_status": row.status},
            )

        self._apply_offer_update(row=row, payload=payload)

        if payload.media_items is not None:
            self.repo.replace_offer_media(
                offer=row,
                rows=self._offer_media_rows(payload.media_items, owner_user_id=user.id),
            )

        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(
                message="Service offer slug already exists for this provider",
                details={"slug": row.slug},
            ) from exc

        self.repo.refresh(row)
        return self._offer_out(row)

    def submit_my_offer(
        self,
        *,
        user: AuthUser,
        offer_id: int,
    ) -> ServiceOfferOut:
        provider = self._get_approved_provider_profile(user)
        row = self._get_owned_offer(provider_profile_id=provider.id, offer_id=offer_id)

        if row.status not in {
            ServiceOfferStatus.DRAFT.value,
            ServiceOfferStatus.REJECTED.value,
        }:
            raise ValidationAuthError(
                message="Service offer cannot be submitted in current status",
                details={"current_status": row.status},
            )

        self._validate_offer_ready(row)

        row.status = ServiceOfferStatus.PENDING_REVIEW.value
        row.submitted_at = datetime.utcnow()
        row.admin_note = None

        self.repo.commit()
        self.repo.refresh(row)
        self._notify_offer_submitted(row)

        return self._offer_out(row)

    def list_admin_offers(
        self,
        *,
        status: str | None,
        category_id: int | None,
        provider_profile_id: int | None,
        pricing_type: str | None,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ServiceOfferOut], int]:
        if status is not None:
            self._validate_offer_status(status)

        if category_id is not None:
            self._validate_offer_category(category_id, require_active=False)

        if pricing_type is not None:
            self._validate_pricing_type(pricing_type)

        rows, total = self.repo.list_admin_offers(
            status=status,
            category_id=category_id,
            provider_profile_id=provider_profile_id,
            pricing_type=pricing_type,
            q=q,
            page=max(page, 1),
            page_size=min(max(page_size, 1), 100),
        )

        return [self._offer_out(row) for row in rows], total

    def get_admin_offer(self, offer_id: int) -> ServiceOfferOut:
        row = self.repo.get_offer_by_id(offer_id)

        if row is None or row.deleted_at is not None:
            raise ValidationAuthError(
                message="Service offer not found",
                details={"offer_id": offer_id},
            )

        return self._offer_out(row)

    def update_offer_status_admin(
        self,
        *,
        offer_id: int,
        admin_user: AuthUser,
        payload: ServiceOfferStatusUpdateIn,
    ) -> ServiceOfferOut:
        status = self._validate_offer_status(payload.status)
        row = self.repo.get_offer_by_id(offer_id)

        if row is None or row.deleted_at is not None:
            raise ValidationAuthError(
                message="Service offer not found",
                details={"offer_id": offer_id},
            )

        now = datetime.utcnow()
        row.status = status
        row.admin_note = payload.note

        if status == ServiceOfferStatus.APPROVED.value:
            row.approved_at = now
            row.approved_by = admin_user.id
            row.rejected_at = None
            row.rejected_by = None
            row.suspended_at = None
            row.suspended_by = None
        elif status == ServiceOfferStatus.REJECTED.value:
            row.rejected_at = now
            row.rejected_by = admin_user.id
        elif status == ServiceOfferStatus.SUSPENDED.value:
            row.suspended_at = now
            row.suspended_by = admin_user.id
        elif status == ServiceOfferStatus.ARCHIVED.value:
            row.suspended_at = None
            row.suspended_by = None

        self.repo.commit()
        self.repo.refresh(row)
        self._notify_offer_status(row, status)

        return self._offer_out(row)

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

    def create_service_request(
        self,
        *,
        user: AuthUser,
        payload: ServiceRequestCreateIn,
    ) -> ServiceRequestDetailOut:
        offer = self.repo.get_public_offer_by_id(payload.offer_id)
        if offer is None:
            raise ValidationAuthError(
                message="Approved service offer not found",
                details={"offer_id": payload.offer_id},
            )

        contact_method = self._validate_request_contact_method(payload.contact_method)
        row = ServiceRequest(
            requester_user_id=user.id,
            provider_profile_id=offer.provider_profile_id,
            offer_id=offer.id,
            category_id=offer.category_id,
            title=payload.title.strip(),
            description=payload.description.strip(),
            contact_method=contact_method,
            status=ServiceRequestStatus.OPEN.value,
            budget_amount=payload.budget_amount,
            currency=payload.currency.upper(),
            scheduled_at=payload.scheduled_at,
            province_id=payload.province_id,
            city_id=payload.city_id,
            village_id=payload.village_id,
            province_name=payload.province_name,
            city_name=payload.city_name,
            village_name=payload.village_name,
            address_text=payload.address_text,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        self.repo.add_request(row)
        self._add_request_status_log(
            request=row,
            changed_by=user.id,
            from_status=None,
            to_status=ServiceRequestStatus.OPEN.value,
            note="Service request created",
        )
        offer.requests_count += 1
        if offer.provider_profile is not None:
            offer.provider_profile.requests_count += 1
        self.repo.commit()
        self.repo.refresh(row)
        return self._request_detail_out(row, include_admin_note=False)

    def list_my_service_requests(
        self,
        *,
        user: AuthUser,
        status: str | None,
        offer_id: int | None,
        category_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ServiceRequestOut], int]:
        if status is not None:
            self._validate_request_status(status)
        rows, total = self.repo.list_requests(
            requester_user_id=user.id,
            status=status,
            offer_id=offer_id,
            category_id=category_id,
            page=max(page, 1),
            page_size=min(max(page_size, 1), 100),
        )
        return [self._request_out(row) for row in rows], total

    def get_my_service_request_detail(
        self,
        *,
        request_id: int,
        user: AuthUser,
    ) -> ServiceRequestDetailOut:
        row = self._get_request(request_id)
        if row.requester_user_id != user.id:
            raise PermissionDeniedError()
        return self._request_detail_out(row, include_admin_note=False)

    def cancel_my_service_request(
        self,
        *,
        request_id: int,
        user: AuthUser,
        payload: ServiceRequestCancelIn,
    ) -> ServiceRequestDetailOut:
        row = self._get_request(request_id)
        if row.requester_user_id != user.id:
            raise PermissionDeniedError()
        if row.status not in {
            ServiceRequestStatus.OPEN.value,
            ServiceRequestStatus.ACCEPTED.value,
        }:
            raise ValidationAuthError(
                message="Service request cannot be cancelled in current status",
                details={"current_status": row.status},
            )
        self._set_request_status(
            row,
            ServiceRequestStatus.CANCELLED.value,
            changed_by=user.id,
            note=payload.reason,
        )
        row.cancel_reason = payload.reason
        self.repo.commit()
        self.repo.refresh(row)
        return self._request_detail_out(row, include_admin_note=False)

    def list_assigned_service_requests(
        self,
        *,
        user: AuthUser,
        status: str | None,
        offer_id: int | None,
        category_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ServiceRequestOut], int]:
        profile = self._approved_request_provider(user)
        if status is not None:
            self._validate_request_status(status)
        rows, total = self.repo.list_requests(
            provider_profile_id=profile.id,
            status=status,
            offer_id=offer_id,
            category_id=category_id,
            page=max(page, 1),
            page_size=min(max(page_size, 1), 100),
        )
        return [self._request_out(row) for row in rows], total

    def get_assigned_service_request_detail(
        self,
        *,
        request_id: int,
        user: AuthUser,
    ) -> ServiceRequestDetailOut:
        profile = self._approved_request_provider(user)
        row = self._get_request(request_id)
        if row.provider_profile_id != profile.id:
            raise PermissionDeniedError()
        return self._request_detail_out(row, include_admin_note=False)

    def update_assigned_service_request_status(
        self,
        *,
        request_id: int,
        user: AuthUser,
        payload: ServiceRequestStatusUpdateIn,
    ) -> ServiceRequestDetailOut:
        profile = self._approved_request_provider(user)
        row = self._get_request(request_id)
        if row.provider_profile_id != profile.id:
            raise PermissionDeniedError()
        target = self._validate_request_status(payload.status)
        self._validate_request_transition(row.status, target, self.PROVIDER_REQUEST_TRANSITIONS)
        self._set_request_status(row, target, changed_by=user.id, note=payload.note)
        row.provider_note = payload.note
        self.repo.commit()
        self.repo.refresh(row)
        return self._request_detail_out(row, include_admin_note=False)

    def list_admin_service_requests(
        self,
        *,
        requester_user_id: int | None,
        provider_user_id: int | None,
        offer_id: int | None,
        category_id: int | None,
        province_id: int | None,
        city_id: int | None,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ServiceRequestOut], int]:
        if status is not None:
            self._validate_request_status(status)
        rows, total = self.repo.list_requests(
            requester_user_id=requester_user_id,
            provider_user_id=provider_user_id,
            offer_id=offer_id,
            category_id=category_id,
            province_id=province_id,
            city_id=city_id,
            status=status,
            page=max(page, 1),
            page_size=min(max(page_size, 1), 100),
        )
        return [self._request_out(row) for row in rows], total

    def get_admin_service_request_detail(self, request_id: int) -> ServiceRequestDetailOut:
        return self._request_detail_out(self._get_request(request_id), include_admin_note=True)

    def update_admin_service_request_status(
        self,
        *,
        request_id: int,
        admin_user: AuthUser,
        payload: ServiceRequestStatusUpdateIn,
    ) -> ServiceRequestDetailOut:
        row = self._get_request(request_id)
        target = self._validate_request_status(payload.status)
        self._validate_request_transition(row.status, target, self.ADMIN_REQUEST_TRANSITIONS)
        self._set_request_status(row, target, changed_by=admin_user.id, note=payload.note)
        row.admin_note = payload.note
        if target == ServiceRequestStatus.CANCELLED.value:
            row.cancel_reason = payload.note
        self.repo.commit()
        self.repo.refresh(row)
        return self._request_detail_out(row, include_admin_note=True)

    def _approved_request_provider(self, user: AuthUser) -> ServiceProviderProfile:
        profile = self.repo.get_profile_by_user_id(user.id)
        if profile is None or profile.status != ServiceProviderStatus.APPROVED.value:
            raise PermissionDeniedError()
        return profile

    def _get_request(self, request_id: int) -> ServiceRequest:
        row = self.repo.get_request_by_id(request_id)
        if row is None:
            raise ValidationAuthError(
                message="Service request not found",
                details={"request_id": request_id},
            )
        return row

    def _validate_request_status(self, status: str) -> str:
        normalized = status.strip().lower()
        allowed = {item.value for item in ServiceRequestStatus}
        if normalized not in allowed:
            raise ValidationAuthError(
                message="Invalid service request status",
                details={"allowed": sorted(allowed)},
            )
        return normalized

    def _validate_request_contact_method(self, method: str) -> str:
        normalized = method.strip().lower()
        allowed = {item.value for item in ServiceContactMethod}
        if normalized not in allowed:
            raise ValidationAuthError(
                message="Invalid service request contact method",
                details={"allowed": sorted(allowed)},
            )
        return normalized

    def _validate_request_transition(
        self,
        current: str,
        target: str,
        transitions: dict[str, set[str]],
    ) -> None:
        if target not in transitions.get(current, set()):
            raise ValidationAuthError(
                message="Invalid service request status transition",
                details={"from_status": current, "to_status": target},
            )

    def _set_request_status(
        self,
        row: ServiceRequest,
        status: str,
        *,
        changed_by: int | None,
        note: str | None,
    ) -> None:
        old_status = row.status
        row.status = status
        now = datetime.utcnow()
        if status == ServiceRequestStatus.ACCEPTED.value and row.accepted_at is None:
            row.accepted_at = now
        elif status == ServiceRequestStatus.COMPLETED.value:
            row.completed_at = row.completed_at or now
            if old_status != ServiceRequestStatus.COMPLETED.value:
                if row.offer is not None:
                    row.offer.completed_requests_count += 1
                if row.provider_profile is not None:
                    row.provider_profile.completed_requests_count += 1
        elif status == ServiceRequestStatus.CANCELLED.value and row.cancelled_at is None:
            row.cancelled_at = now
        self._add_request_status_log(
            request=row,
            changed_by=changed_by,
            from_status=old_status,
            to_status=status,
            note=note,
        )

    def _add_request_status_log(
        self,
        *,
        request: ServiceRequest,
        changed_by: int | None,
        from_status: str | None,
        to_status: str,
        note: str | None,
    ) -> None:
        self.repo.add_request_status_log(
            ServiceRequestStatusLog(
                request_id=request.id,
                changed_by=changed_by,
                from_status=from_status,
                to_status=to_status,
                note=note,
            )
        )

    def _request_out(self, row: ServiceRequest) -> ServiceRequestOut:
        return ServiceRequestOut.model_validate(row)

    def _request_detail_out(
        self,
        row: ServiceRequest,
        *,
        include_admin_note: bool,
    ) -> ServiceRequestDetailOut:
        logs = self.repo.list_request_status_logs(row.id)
        return ServiceRequestDetailOut(
            **self._request_out(row).model_dump(),
            address_text=row.address_text,
            latitude=row.latitude,
            longitude=row.longitude,
            provider_note=row.provider_note,
            admin_note=row.admin_note if include_admin_note else None,
            cancel_reason=row.cancel_reason,
            status_logs=[ServiceRequestStatusLogOut.model_validate(log) for log in logs],
        )

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

    def _get_approved_provider_profile(self, user: AuthUser) -> ServiceProviderProfile:
        profile = self.repo.get_profile_by_user_id(user.id)

        if (
            profile is None
            or profile.deleted_at is not None
            or profile.status != ServiceProviderStatus.APPROVED.value
        ):
            raise ValidationAuthError(
                message="Approved service provider profile is required",
                details={"user_id": user.id},
            )

        return profile

    def _get_owned_offer(
        self,
        *,
        provider_profile_id: int,
        offer_id: int,
    ) -> ServiceOffer:
        row = self.repo.get_offer_by_id(offer_id)

        if (
            row is None
            or row.deleted_at is not None
            or row.provider_profile_id != provider_profile_id
        ):
            raise ValidationAuthError(
                message="Service offer not found",
                details={"offer_id": offer_id},
            )

        return row

    def _apply_offer_update(
        self,
        *,
        row: ServiceOffer,
        payload: ServiceOfferUpdateIn,
    ) -> None:
        fields = payload.model_fields_set

        if "category_id" in fields:
            if payload.category_id is not None:
                self._validate_offer_category(payload.category_id, require_active=True)
            row.category_id = payload.category_id
        if "title" in fields:
            row.title = payload.title.strip() if payload.title else row.title
        if "slug" in fields and payload.slug is not None:
            row.slug = self._normalize_slug(payload.slug)
        if "short_description" in fields:
            row.short_description = payload.short_description
        if "description" in fields:
            row.description = payload.description
        if "pricing_type" in fields and payload.pricing_type is not None:
            row.pricing_type = self._validate_pricing_type(payload.pricing_type)
        if "price_amount" in fields:
            row.price_amount = payload.price_amount
        if "currency" in fields and payload.currency is not None:
            row.currency = payload.currency.upper()
        if "province_id" in fields:
            row.province_id = payload.province_id
        if "city_id" in fields:
            row.city_id = payload.city_id
        if "village_id" in fields:
            row.village_id = payload.village_id
        if "province_name" in fields:
            row.province_name = payload.province_name
        if "city_name" in fields:
            row.city_name = payload.city_name
        if "village_name" in fields:
            row.village_name = payload.village_name
        if "service_area" in fields:
            row.service_area = payload.service_area
        if "latitude" in fields:
            row.latitude = payload.latitude
        if "longitude" in fields:
            row.longitude = payload.longitude
        if "is_active" in fields and payload.is_active is not None:
            row.is_active = payload.is_active

        self._validate_offer_price(
            pricing_type=row.pricing_type,
            price_amount=row.price_amount,
        )

    def _offer_media_rows(
        self,
        items: list[ServiceOfferMediaIn],
        *,
        owner_user_id: int,
    ) -> list[ServiceOfferMedia]:
        primary_count = sum(1 for item in items if item.is_primary)

        if primary_count > 1:
            raise ValidationAuthError(
                message="Only one primary service offer media item is allowed",
            )

        rows: list[ServiceOfferMedia] = []

        for item in items:
            self._validate_offer_media_payload(item, owner_user_id=owner_user_id)
            rows.append(
                ServiceOfferMedia(
                    file_id=item.file_id,
                    media_file_id=item.media_file_id,
                    file_path=item.file_path,
                    alt_text=item.alt_text,
                    sort_order=item.sort_order,
                    is_primary=item.is_primary,
                )
            )

        if rows and primary_count == 0:
            rows[0].is_primary = True

        return rows

    def _validate_offer_media_payload(
        self,
        item: ServiceOfferMediaIn,
        *,
        owner_user_id: int,
    ) -> None:
        if item.file_id is None and item.media_file_id is None and item.file_path is None:
            raise ValidationAuthError(
                message="Service offer media must reference a file",
            )

        if item.media_file_id is None:
            return

        media = self.repo.get_media_file_by_id(item.media_file_id)
        if media is None or media.owner_user_id != owner_user_id:
            raise ValidationAuthError(
                message="Service offer media file not found",
                details={"media_file_id": item.media_file_id},
            )

        if media.status != MediaStatus.ACTIVE.value:
            raise ValidationAuthError(
                message="Service offer media file is not active",
                details={"media_file_id": item.media_file_id},
            )

        if media.visibility != MediaVisibility.PUBLIC.value:
            raise ValidationAuthError(
                message="Service offer media must be public",
                details={"media_file_id": item.media_file_id},
            )

    def _validate_offer_ready(self, row: ServiceOffer) -> None:
        missing = []
        if not row.category_id:
            missing.append("category_id")
        if not row.title:
            missing.append("title")
        if not row.slug:
            missing.append("slug")
        if not row.short_description:
            missing.append("short_description")
        if not row.description:
            missing.append("description")

        self._validate_offer_price(
            pricing_type=row.pricing_type,
            price_amount=row.price_amount,
        )

        if missing:
            raise ValidationAuthError(
                message="Service offer is not ready for review",
                details={"missing": missing},
            )

    def _offer_out(self, row: ServiceOffer) -> ServiceOfferOut:
        media = [
            self._media_out(item)
            for item in sorted(row.media or [], key=lambda item: (item.sort_order, item.id))
        ]
        primary_media = next((item for item in media if item.is_primary), media[0] if media else None)

        category = None
        if row.category is not None:
            category = ServiceCategoryOut.model_validate(row.category)

        provider = None
        if row.provider_profile is not None:
            provider = self._public_profile_out(row.provider_profile)

        return ServiceOfferOut(
            id=row.id,
            provider_profile_id=row.provider_profile_id,
            category_id=row.category_id,
            title=row.title,
            slug=row.slug,
            short_description=row.short_description,
            description=row.description,
            status=row.status,
            pricing_type=row.pricing_type,
            price_amount=row.price_amount,
            currency=row.currency,
            province_id=row.province_id,
            city_id=row.city_id,
            village_id=row.village_id,
            province_name=row.province_name,
            city_name=row.city_name,
            village_name=row.village_name,
            service_area=row.service_area,
            latitude=row.latitude,
            longitude=row.longitude,
            is_active=row.is_active,
            is_featured=row.is_featured,
            views_count=row.views_count,
            requests_count=row.requests_count,
            completed_requests_count=row.completed_requests_count,
            media=media,
            primary_media=primary_media,
            category=category,
            provider=provider,
            admin_note=row.admin_note,
            submitted_at=row.submitted_at,
            approved_at=row.approved_at,
            approved_by=row.approved_by,
            rejected_at=row.rejected_at,
            rejected_by=row.rejected_by,
            suspended_at=row.suspended_at,
            suspended_by=row.suspended_by,
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
        )

    def _public_offer_out(self, row: ServiceOffer) -> ServiceOfferPublicOut:
        return ServiceOfferPublicOut.model_validate(self._offer_out(row).model_dump())

    def _media_out(self, row: ServiceOfferMedia) -> ServiceOfferMediaOut:
        file_key = None
        public_url = None

        if row.media_file_id is not None:
            media = self.repo.get_media_file_by_id(row.media_file_id)
            if media is not None:
                file_key = media.file_key
                if file_key:
                    public_url = f"/api/v1/media/public/{file_key}"

        return ServiceOfferMediaOut(
            id=row.id,
            offer_id=row.offer_id,
            file_id=row.file_id,
            media_file_id=row.media_file_id,
            file_key=file_key,
            public_url=public_url,
            file_path=row.file_path,
            alt_text=row.alt_text,
            sort_order=row.sort_order,
            is_primary=row.is_primary,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def _normalize_slug(self, slug: str) -> str:
        clean = slug.strip().lower().replace(" ", "-")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,158}[a-z0-9]", clean):
            raise ValidationAuthError(
                message="Invalid service offer slug",
                details={"format": "lowercase letters, numbers, underscore or dash"},
            )
        return clean

    def _validate_pricing_type(self, pricing_type: str) -> str:
        allowed = {item.value for item in ServicePricingType}
        if pricing_type not in allowed:
            raise ValidationAuthError(
                message="Invalid service offer pricing type",
                details={"allowed": sorted(allowed)},
            )
        return pricing_type

    def _validate_offer_status(self, status: str) -> str:
        allowed = {item.value for item in ServiceOfferStatus}
        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid service offer status",
                details={"allowed": sorted(allowed)},
            )
        return status

    def _validate_offer_category(
        self,
        category_id: int,
        *,
        require_active: bool,
    ) -> None:
        category = self.repo.get_category_by_id(category_id)
        if category is None or (require_active and not category.is_active):
            raise ValidationAuthError(
                message="Service category not found",
                details={"category_id": category_id},
            )

    def _validate_offer_price(
        self,
        *,
        pricing_type: str,
        price_amount: Decimal | None,
    ) -> None:
        if pricing_type == ServicePricingType.NEGOTIABLE.value:
            return

        if price_amount is None:
            raise ValidationAuthError(
                message="Service offer price amount is required",
                details={"pricing_type": pricing_type},
            )

    def _notify_offer_submitted(self, row: ServiceOffer) -> None:
        admin_ids = self.repo.list_service_admin_recipient_user_ids()
        if not admin_ids:
            return

        provider_user_id = row.provider_profile.user_id if row.provider_profile else None

        NotificationService(self.db).create_event_and_notify_many(
            event_type=NotificationEventType.SERVICE_OFFER_SUBMITTED.value,
            recipient_user_ids=admin_ids,
            title="خدمت جدید برای بررسی",
            body=f"خدمت «{row.title}» برای بررسی ارسال شد.",
            actor_user_id=provider_user_id,
            source_type="service_offer",
            source_id=str(row.id),
            payload_json={
                "offer_id": row.id,
                "provider_profile_id": row.provider_profile_id,
            },
            action_url=f"/admin/services/offers?offer_id={row.id}",
            priority=NotificationPriority.HIGH.value,
            commit=True,
        )

    def _notify_offer_status(self, row: ServiceOffer, status: str) -> None:
        if row.provider_profile is None:
            return

        if status == ServiceOfferStatus.APPROVED.value:
            event_type = NotificationEventType.SERVICE_OFFER_APPROVED.value
            title = "خدمت شما تأیید شد"
            body = f"خدمت «{row.title}» در بازار خدمات منتشر شد."
        elif status == ServiceOfferStatus.REJECTED.value:
            event_type = NotificationEventType.SERVICE_OFFER_REJECTED.value
            title = "خدمت شما رد شد"
            body = row.admin_note or f"خدمت «{row.title}» نیاز به اصلاح دارد."
        else:
            return

        NotificationService(self.db).create_event_and_notify_user(
            event_type=event_type,
            recipient_user_id=row.provider_profile.user_id,
            title=title,
            body=body,
            actor_user_id=row.approved_by or row.rejected_by or row.suspended_by,
            source_type="service_offer",
            source_id=str(row.id),
            payload_json={"offer_id": row.id, "status": status},
            action_url=f"/services/me/offers/{row.id}",
            priority=NotificationPriority.HIGH.value,
            commit=True,
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
