from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository
from app.modules.consultants.enums import (
    ConsultContactMethod,
    ConsultProfileStatus,
    ConsultRequestStatus,
)
from app.modules.consultants.models import (
    ConsultProfile,
    ConsultRequest,
    ConsultRequestStatusLog,
    ConsultSpecialty,
)
from app.modules.consultants.repository import ConsultantRepository
from app.modules.consultants.schemas import (
    ConsultProfileCreateIn,
    ConsultProfileOut,
    ConsultProfilePublicOut,
    ConsultProfileStatusUpdateIn,
    ConsultProfileUpdateIn,
    ConsultRequestCreateIn,
    ConsultRequestOut,
    ConsultRequestStatusLogOut,
    ConsultRequestStatusUpdateIn,
    ConsultSpecialtyCreateIn,
    ConsultSpecialtyOut,
    ConsultSpecialtyUpdateIn,
)
from app.modules.media.enums import MediaStatus, MediaVisibility
from app.modules.notifications.enums import NotificationEventType, NotificationPriority
from app.modules.notifications.service import NotificationService


class ConsultantService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ConsultantRepository(db)
        self.auth_repo = AuthRepository(db)

    def list_specialties(
        self,
        *,
        active_only: bool = True,
        q: str | None = None,
    ) -> list[ConsultSpecialtyOut]:
        return [
            ConsultSpecialtyOut.model_validate(row)
            for row in self.repo.list_specialties(active_only=active_only, q=q)
        ]

    def create_specialty(self, payload: ConsultSpecialtyCreateIn) -> ConsultSpecialtyOut:
        code = self._normalize_code(payload.code)

        row = ConsultSpecialty(
            code=code,
            title=payload.title.strip(),
            description=payload.description,
            sort_order=payload.sort_order,
            is_active=payload.is_active,
        )

        self.repo.add_specialty(row)

        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(
                message="Consult specialty code already exists",
                details={"code": code},
            ) from exc

        self.repo.refresh(row)
        return ConsultSpecialtyOut.model_validate(row)

    def update_specialty(
        self,
        *,
        specialty_id: int,
        payload: ConsultSpecialtyUpdateIn,
    ) -> ConsultSpecialtyOut:
        row = self.repo.get_specialty_by_id(specialty_id)

        if row is None:
            raise ValidationAuthError(
                message="Consult specialty not found",
                details={"specialty_id": specialty_id},
            )

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
                message="Consult specialty code already exists",
                details={"code": row.code},
            ) from exc

        self.repo.refresh(row)
        return ConsultSpecialtyOut.model_validate(row)

    def get_my_profile(self, user: AuthUser) -> ConsultProfileOut | None:
        profile = self.repo.get_profile_by_user_id(user.id)
        return self._profile_out(profile) if profile else None

    def create_or_update_my_profile(
        self,
        *,
        user: AuthUser,
        payload: ConsultProfileCreateIn | ConsultProfileUpdateIn,
    ) -> ConsultProfileOut:
        self._validate_specialty_ids(payload.specialty_ids, require_active=True)
        self._validate_avatar_media(
            media_file_id=payload.avatar_media_file_id,
            owner_user_id=user.id,
        )

        profile = self.repo.get_profile_by_user_id(user.id)
        if profile is None:
            profile = ConsultProfile(user_id=user.id, status=ConsultProfileStatus.DRAFT.value)
            self.repo.add_profile(profile)

        if profile.status == ConsultProfileStatus.SUSPENDED.value:
            raise ValidationAuthError(
                message="Suspended consultant profile cannot be updated",
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
        profile.province_name = payload.province_name
        profile.city_name = payload.city_name
        profile.avatar_file_id = payload.avatar_file_id
        profile.avatar_media_file_id = payload.avatar_media_file_id

        self.repo.replace_profile_specialties(
            profile=profile,
            specialty_ids=self._unique_ids(payload.specialty_ids),
        )

        self.repo.commit()
        self.repo.refresh(profile)
        return self._profile_out(profile)

    def submit_my_profile(self, user: AuthUser) -> ConsultProfileOut:
        profile = self.repo.get_profile_by_user_id(user.id)

        if profile is None:
            raise ValidationAuthError(message="Consultant profile not found")

        if profile.status not in {
            ConsultProfileStatus.DRAFT.value,
            ConsultProfileStatus.REJECTED.value,
        }:
            raise ValidationAuthError(
                message="Consultant profile cannot be submitted in current status",
                details={"current_status": profile.status},
            )

        missing = []
        if not self._resolved_display_name(profile):
            missing.append("display_name")
        if not profile.title:
            missing.append("title")
        if not profile.bio:
            missing.append("bio")
        if not profile.specialty_links:
            missing.append("specialty_ids")

        if missing:
            raise ValidationAuthError(
                message="Consultant profile is not ready for review",
                details={"missing": missing},
            )

        profile.status = ConsultProfileStatus.PENDING_REVIEW.value
        profile.submitted_at = datetime.utcnow()
        profile.admin_note = None

        self.repo.commit()
        self.repo.refresh(profile)
        self._notify_profile_submitted(profile)

        return self._profile_out(profile)

    def list_public_profiles(
        self,
        *,
        specialty_id: int | None,
        q: str | None,
        province_id: int | None,
        city_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ConsultProfilePublicOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if specialty_id is not None:
            specialty = self.repo.get_specialty_by_id(specialty_id)
            if specialty is None or not specialty.is_active:
                raise ValidationAuthError(
                    message="Consult specialty not found",
                    details={"specialty_id": specialty_id},
                )

        rows, total = self.repo.list_profiles(
            public_only=True,
            specialty_id=specialty_id,
            q=q,
            province_id=province_id,
            city_id=city_id,
            page=page,
            page_size=page_size,
        )

        return [self._public_profile_out(row) for row in rows], total

    def get_public_profile(self, profile_id: int) -> ConsultProfilePublicOut:
        profile = self.repo.get_profile_by_id(profile_id)

        if (
            profile is None
            or profile.deleted_at is not None
            or profile.status != ConsultProfileStatus.APPROVED.value
        ):
            raise ValidationAuthError(
                message="Consultant profile not found",
                details={"profile_id": profile_id},
            )

        return self._public_profile_out(profile)

    def list_admin_profiles(
        self,
        *,
        status: str | None,
        specialty_id: int | None,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ConsultProfileOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_profile_status(status)

        rows, total = self.repo.list_profiles(
            status=status,
            specialty_id=specialty_id,
            q=q,
            page=page,
            page_size=page_size,
        )

        return [self._profile_out(row) for row in rows], total

    def get_admin_profile(self, profile_id: int) -> ConsultProfileOut:
        profile = self.repo.get_profile_by_id(profile_id)

        if profile is None or profile.deleted_at is not None:
            raise ValidationAuthError(
                message="Consultant profile not found",
                details={"profile_id": profile_id},
            )

        return self._profile_out(profile)

    def update_profile_status_admin(
        self,
        *,
        profile_id: int,
        admin_user: AuthUser,
        payload: ConsultProfileStatusUpdateIn,
    ) -> ConsultProfileOut:
        status = self._validate_profile_status(payload.status)
        profile = self.repo.get_profile_by_id(profile_id)

        if profile is None or profile.deleted_at is not None:
            raise ValidationAuthError(
                message="Consultant profile not found",
                details={"profile_id": profile_id},
            )

        now = datetime.utcnow()
        profile.status = status
        profile.admin_note = payload.note

        if status == ConsultProfileStatus.APPROVED.value:
            profile.approved_at = now
            profile.approved_by = admin_user.id
            profile.rejected_at = None
            profile.rejected_by = None
            profile.suspended_at = None
            profile.suspended_by = None
            self._assign_consultant_role(profile.user_id, assigned_by=admin_user.id)
        elif status == ConsultProfileStatus.REJECTED.value:
            profile.rejected_at = now
            profile.rejected_by = admin_user.id
        elif status == ConsultProfileStatus.SUSPENDED.value:
            profile.suspended_at = now
            profile.suspended_by = admin_user.id

        self.repo.commit()
        self.repo.refresh(profile)
        self._notify_profile_status(profile, status)

        return self._profile_out(profile)

    def create_request(
        self,
        *,
        user: AuthUser,
        payload: ConsultRequestCreateIn,
    ) -> ConsultRequestOut:
        contact_method = self._validate_contact_method(payload.contact_method)

        consultant = None
        if payload.consultant_profile_id is not None:
            consultant = self.repo.get_profile_by_id(payload.consultant_profile_id)
            if (
                consultant is None
                or consultant.deleted_at is not None
                or consultant.status != ConsultProfileStatus.APPROVED.value
            ):
                raise ValidationAuthError(
                    message="Consultant profile not found",
                    details={"consultant_profile_id": payload.consultant_profile_id},
                )

        specialty = None
        if payload.specialty_id is not None:
            specialty = self.repo.get_specialty_by_id(payload.specialty_id)
            if specialty is None or not specialty.is_active:
                raise ValidationAuthError(
                    message="Consult specialty not found",
                    details={"specialty_id": payload.specialty_id},
                )

        if consultant is not None and payload.specialty_id is not None:
            consultant_specialty_ids = {
                link.specialty_id for link in consultant.specialty_links
            }
            if payload.specialty_id not in consultant_specialty_ids:
                raise ValidationAuthError(
                    message="Selected consultant does not provide this specialty",
                    details={
                        "consultant_profile_id": consultant.id,
                        "specialty_id": payload.specialty_id,
                    },
                )

        row = ConsultRequest(
            requester_user_id=user.id,
            consultant_profile_id=consultant.id if consultant else None,
            specialty_id=specialty.id if specialty else None,
            title=payload.title.strip(),
            description=payload.description.strip(),
            contact_method=contact_method,
            status=ConsultRequestStatus.OPEN.value,
            budget_amount=payload.budget_amount,
            currency=payload.currency.upper(),
            scheduled_at=payload.scheduled_at,
        )

        self.repo.add_request(row)
        self._add_request_status_log(
            request=row,
            changed_by=user.id,
            from_status=None,
            to_status=ConsultRequestStatus.OPEN.value,
            note="Consult request created",
        )

        if consultant is not None:
            consultant.requests_count += 1

        self.repo.commit()
        self.repo.refresh(row)
        self._notify_request_created(row)

        return self._request_out(row)

    def list_my_requests(
        self,
        *,
        user: AuthUser,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ConsultRequestOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_request_status(status)

        rows, total = self.repo.list_requests(
            requester_user_id=user.id,
            status=status,
            page=page,
            page_size=page_size,
        )
        return [self._request_out(row) for row in rows], total

    def list_my_consultant_requests(
        self,
        *,
        user: AuthUser,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ConsultRequestOut], int]:
        profile = self.repo.get_profile_by_user_id(user.id)
        if profile is None or profile.status != ConsultProfileStatus.APPROVED.value:
            raise ValidationAuthError(message="Approved consultant profile is required")

        if status is not None:
            self._validate_request_status(status)

        rows, total = self.repo.list_requests(
            consultant_profile_id=profile.id,
            status=status,
            page=max(page, 1),
            page_size=min(max(page_size, 1), 100),
        )
        return [self._request_out(row) for row in rows], total

    def update_consultant_request_status(
        self,
        *,
        request_id: int,
        user: AuthUser,
        payload: ConsultRequestStatusUpdateIn,
    ) -> ConsultRequestOut:
        profile = self.repo.get_profile_by_user_id(user.id)
        if profile is None or profile.status != ConsultProfileStatus.APPROVED.value:
            raise ValidationAuthError(message="Approved consultant profile is required")

        row = self.repo.get_request_by_id(request_id)
        if row is None or row.consultant_profile_id != profile.id:
            raise ValidationAuthError(
                message="Consult request not found",
                details={"request_id": request_id},
            )

        target_status = self._validate_request_status(payload.status)
        allowed = {
            ConsultRequestStatus.OPEN.value: {
                ConsultRequestStatus.ACCEPTED.value,
                ConsultRequestStatus.REJECTED.value,
            },
            ConsultRequestStatus.ACCEPTED.value: {
                ConsultRequestStatus.IN_PROGRESS.value,
                ConsultRequestStatus.CANCELLED.value,
            },
            ConsultRequestStatus.IN_PROGRESS.value: {
                ConsultRequestStatus.COMPLETED.value,
                ConsultRequestStatus.CANCELLED.value,
            },
        }

        if target_status not in allowed.get(row.status, set()):
            raise ValidationAuthError(
                message="Invalid consult request status transition",
                details={"from_status": row.status, "to_status": target_status},
            )

        self._set_request_status(row, target_status, changed_by=user.id, note=payload.note)
        self.repo.commit()
        self.repo.refresh(row)
        self._notify_request_status(row, target_status)
        return self._request_out(row)

    def cancel_my_request(
        self,
        *,
        request_id: int,
        user: AuthUser,
        payload: ConsultRequestStatusUpdateIn,
    ) -> ConsultRequestOut:
        row = self.repo.get_request_by_id(request_id)
        if row is None or row.requester_user_id != user.id:
            raise ValidationAuthError(
                message="Consult request not found",
                details={"request_id": request_id},
            )

        if row.status not in {
            ConsultRequestStatus.OPEN.value,
            ConsultRequestStatus.ACCEPTED.value,
            ConsultRequestStatus.IN_PROGRESS.value,
        }:
            raise ValidationAuthError(
                message="Consult request cannot be cancelled in current status",
                details={"current_status": row.status},
            )

        self._set_request_status(
            row,
            ConsultRequestStatus.CANCELLED.value,
            changed_by=user.id,
            note=payload.note,
        )
        row.cancel_reason = payload.note

        self.repo.commit()
        self.repo.refresh(row)
        self._notify_request_status(row, ConsultRequestStatus.CANCELLED.value)
        return self._request_out(row)

    def list_admin_requests(
        self,
        *,
        requester_user_id: int | None,
        consultant_profile_id: int | None,
        specialty_id: int | None,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ConsultRequestOut], int]:
        if status is not None:
            self._validate_request_status(status)

        rows, total = self.repo.list_requests(
            requester_user_id=requester_user_id,
            consultant_profile_id=consultant_profile_id,
            specialty_id=specialty_id,
            status=status,
            page=max(page, 1),
            page_size=min(max(page_size, 1), 100),
        )
        return [self._request_out(row) for row in rows], total

    def update_request_status_admin(
        self,
        *,
        request_id: int,
        admin_user: AuthUser,
        payload: ConsultRequestStatusUpdateIn,
    ) -> ConsultRequestOut:
        row = self.repo.get_request_by_id(request_id)
        if row is None:
            raise ValidationAuthError(
                message="Consult request not found",
                details={"request_id": request_id},
            )

        target_status = self._validate_request_status(payload.status)
        self._set_request_status(row, target_status, changed_by=admin_user.id, note=payload.note)
        row.admin_note = payload.note

        self.repo.commit()
        self.repo.refresh(row)
        self._notify_request_status(row, target_status)
        return self._request_out(row)

    def _set_request_status(
        self,
        row: ConsultRequest,
        status: str,
        *,
        changed_by: int | None,
        note: str | None,
    ) -> None:
        old_status = row.status
        row.status = status

        now = datetime.utcnow()
        if status == ConsultRequestStatus.ACCEPTED.value and row.accepted_at is None:
            row.accepted_at = now
        elif status == ConsultRequestStatus.COMPLETED.value:
            row.completed_at = row.completed_at or now
            if (
                old_status != ConsultRequestStatus.COMPLETED.value
                and row.consultant_profile is not None
            ):
                row.consultant_profile.completed_requests_count += 1
        elif status == ConsultRequestStatus.CANCELLED.value and row.cancelled_at is None:
            row.cancelled_at = now

        if changed_by == (row.consultant_profile.user_id if row.consultant_profile else None):
            row.consultant_note = note

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
        request: ConsultRequest,
        changed_by: int | None,
        from_status: str | None,
        to_status: str,
        note: str | None,
    ) -> None:
        self.repo.add_request_status_log(
            ConsultRequestStatusLog(
                request_id=request.id,
                changed_by=changed_by,
                from_status=from_status,
                to_status=to_status,
                note=note,
            )
        )

    def _profile_out(self, profile: ConsultProfile) -> ConsultProfileOut:
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

        specialties = [
            ConsultSpecialtyOut.model_validate(link.specialty)
            for link in profile.specialty_links
            if link.specialty is not None
        ]

        return ConsultProfileOut(
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
            province_name=profile.province_name,
            city_name=profile.city_name,
            avatar_file_id=avatar_file_id,
            avatar_media_file_id=profile.avatar_media_file_id,
            avatar_url=avatar_url,
            status=profile.status,
            is_verified=profile.status == ConsultProfileStatus.APPROVED.value,
            verification_status=profile.status,
            is_featured=profile.is_featured,
            rating_average=profile.rating_average or Decimal("0.00"),
            reviews_count=profile.reviews_count,
            requests_count=profile.requests_count,
            completed_requests_count=profile.completed_requests_count,
            specialties=specialties,
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

    def _public_profile_out(self, profile: ConsultProfile) -> ConsultProfilePublicOut:
        return ConsultProfilePublicOut.model_validate(
            self._profile_out(profile).model_dump()
        )

    def _request_out(self, row: ConsultRequest) -> ConsultRequestOut:
        logs = sorted(row.status_logs, key=lambda item: item.created_at)
        return ConsultRequestOut(
            id=row.id,
            requester_user_id=row.requester_user_id,
            consultant_profile_id=row.consultant_profile_id,
            specialty_id=row.specialty_id,
            title=row.title,
            description=row.description,
            contact_method=row.contact_method,
            status=row.status,
            budget_amount=row.budget_amount,
            currency=row.currency,
            scheduled_at=row.scheduled_at,
            admin_note=row.admin_note,
            consultant_note=row.consultant_note,
            cancel_reason=row.cancel_reason,
            accepted_at=row.accepted_at,
            completed_at=row.completed_at,
            cancelled_at=row.cancelled_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
            consultant=self._profile_out(row.consultant_profile)
            if row.consultant_profile is not None
            else None,
            specialty=ConsultSpecialtyOut.model_validate(row.specialty)
            if row.specialty is not None
            else None,
            status_logs=[ConsultRequestStatusLogOut.model_validate(log) for log in logs],
        )

    def _resolved_display_name(self, profile: ConsultProfile) -> str | None:
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

    def _validate_specialty_ids(
        self,
        specialty_ids: list[int],
        *,
        require_active: bool,
    ) -> None:
        unique_ids = self._unique_ids(specialty_ids)
        if len(unique_ids) != len(specialty_ids):
            raise ValidationAuthError(message="Duplicate specialty_ids are not allowed")

        for specialty_id in unique_ids:
            specialty = self.repo.get_specialty_by_id(specialty_id)
            if specialty is None or (require_active and not specialty.is_active):
                raise ValidationAuthError(
                    message="Consult specialty not found",
                    details={"specialty_id": specialty_id},
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
                message="Consultant avatar must be public",
                details={"avatar_media_file_id": media_file_id},
            )

    def _normalize_code(self, code: str) -> str:
        clean = code.strip().lower().replace(" ", "_")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,98}[a-z0-9]", clean):
            raise ValidationAuthError(
                message="Invalid consult specialty code",
                details={"format": "lowercase letters, numbers, underscore or dash"},
            )
        return clean

    def _validate_profile_status(self, status: str) -> str:
        allowed = {item.value for item in ConsultProfileStatus}
        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid consultant profile status",
                details={"allowed": sorted(allowed)},
            )
        return status

    def _validate_request_status(self, status: str) -> str:
        allowed = {item.value for item in ConsultRequestStatus}
        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid consult request status",
                details={"allowed": sorted(allowed)},
            )
        return status

    def _validate_contact_method(self, contact_method: str) -> str:
        allowed = {item.value for item in ConsultContactMethod}
        if contact_method not in allowed:
            raise ValidationAuthError(
                message="Invalid consult contact method",
                details={"allowed": sorted(allowed)},
            )
        return contact_method

    def _assign_consultant_role(self, user_id: int, *, assigned_by: int) -> None:
        role = self.auth_repo.get_role_by_code("consultant")
        if role is None:
            return
        self.auth_repo.assign_role_to_user(
            user_id=user_id,
            role_id=role.id,
            assigned_by=assigned_by,
        )

    def _notify_profile_submitted(self, profile: ConsultProfile) -> None:
        admin_ids = self.repo.list_consultant_admin_recipient_user_ids()
        if not admin_ids:
            return

        NotificationService(self.db).create_event_and_notify_many(
            event_type=NotificationEventType.CONSULTANT_REQUEST_SUBMITTED.value,
            recipient_user_ids=admin_ids,
            title="درخواست مشاور جدید",
            body=f"کاربر #{profile.user_id} پروفایل مشاور خود را برای بررسی ارسال کرد.",
            actor_user_id=profile.user_id,
            source_type="consult_profile",
            source_id=str(profile.id),
            payload_json={"profile_id": profile.id, "user_id": profile.user_id},
            action_url=f"/admin/consultants?profile_id={profile.id}",
            priority=NotificationPriority.HIGH.value,
            commit=True,
        )

    def _notify_profile_status(self, profile: ConsultProfile, status: str) -> None:
        if status == ConsultProfileStatus.APPROVED.value:
            event_type = NotificationEventType.CONSULTANT_APPROVED.value
            title = "پروفایل مشاور شما تأیید شد"
            body = "پروفایل مشاور شما فعال شد و در لیست مشاوران نمایش داده می‌شود."
        elif status == ConsultProfileStatus.REJECTED.value:
            event_type = NotificationEventType.CONSULTANT_REJECTED.value
            title = "پروفایل مشاور شما رد شد"
            body = profile.admin_note or "پروفایل مشاور شما نیاز به اصلاح دارد."
        else:
            event_type = NotificationEventType.CONSULTANT_REJECTED.value
            title = "وضعیت پروفایل مشاور تغییر کرد"
            body = f"وضعیت پروفایل مشاور شما به {status} تغییر کرد."

        NotificationService(self.db).create_event_and_notify_user(
            event_type=event_type.value,
            recipient_user_id=profile.user_id,
            title=title,
            body=body,
            actor_user_id=profile.approved_by or profile.rejected_by or profile.suspended_by,
            source_type="consult_profile",
            source_id=str(profile.id),
            payload_json={"profile_id": profile.id, "status": status},
            action_url="/consultants/me/profile",
            priority=NotificationPriority.HIGH.value,
            commit=True,
        )

    def _notify_request_created(self, row: ConsultRequest) -> None:
        if row.consultant_profile is not None:
            recipient_ids = [row.consultant_profile.user_id]
        else:
            recipient_ids = self.repo.list_consultant_admin_recipient_user_ids()

        if not recipient_ids:
            return

        NotificationService(self.db).create_event_and_notify_many(
            event_type=NotificationEventType.CONSULT_REQUEST_CREATED.value,
            recipient_user_ids=recipient_ids,
            title="درخواست مشاوره جدید",
            body=f"درخواست مشاوره «{row.title}» ثبت شد.",
            actor_user_id=row.requester_user_id,
            source_type="consult_request",
            source_id=str(row.id),
            payload_json={
                "request_id": row.id,
                "requester_user_id": row.requester_user_id,
                "consultant_profile_id": row.consultant_profile_id,
                "specialty_id": row.specialty_id,
            },
            action_url=f"/admin/consultants?request_id={row.id}",
            priority=NotificationPriority.NORMAL.value,
            commit=True,
        )

    def _notify_request_status(self, row: ConsultRequest, status: str) -> None:
        event_by_status = {
            ConsultRequestStatus.ACCEPTED.value: NotificationEventType.CONSULT_REQUEST_ACCEPTED,
            ConsultRequestStatus.COMPLETED.value: NotificationEventType.CONSULT_REQUEST_COMPLETED,
            ConsultRequestStatus.CANCELLED.value: NotificationEventType.CONSULT_REQUEST_CANCELLED,
            ConsultRequestStatus.REJECTED.value: NotificationEventType.CONSULT_REQUEST_CANCELLED,
        }
        event_type = event_by_status.get(status)
        if event_type is None:
            return

        recipient_ids = [row.requester_user_id]
        if row.consultant_profile is not None:
            recipient_ids.append(row.consultant_profile.user_id)

        NotificationService(self.db).create_event_and_notify_many(
            event_type=event_type.value,
            recipient_user_ids=recipient_ids,
            title="وضعیت درخواست مشاوره تغییر کرد",
            body=f"درخواست «{row.title}» به وضعیت {status} تغییر کرد.",
            actor_user_id=None,
            source_type="consult_request",
            source_id=str(row.id),
            payload_json={"request_id": row.id, "status": status},
            action_url=f"/consultants/requests/{row.id}",
            priority=NotificationPriority.NORMAL.value,
            commit=True,
        )

    def _unique_ids(self, values: list[int]) -> list[int]:
        return list(dict.fromkeys(values))
