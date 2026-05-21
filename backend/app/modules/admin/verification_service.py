from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.admin.schemas import (
    AdminVerificationDocumentOut,
    AdminVerificationRequestOut,
    AdminVerificationReviewOut,
)
from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository
from app.modules.profiles.enums import VerificationStatus, VerificationTargetRole
from app.modules.profiles.models import VerificationRequest
from app.modules.profiles.repository import ProfileRepository


class AdminVerificationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.profile_repo = ProfileRepository(db)
        self.auth_repo = AuthRepository(db)

    def list_verifications(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        target_role: str | None = None,
        user_id: int | None = None,
    ) -> tuple[list[AdminVerificationRequestOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status:
            self._validate_status_for_filter(status)

        if target_role:
            self._validate_target_role(target_role)

        items, total = self.profile_repo.list_verification_requests(
            status=status,
            target_role=target_role,
            user_id=user_id,
            page=page,
            page_size=page_size,
        )

        return [self._verification_out(item) for item in items], total

    def get_verification_detail(
        self,
        *,
        request_id: int,
    ) -> AdminVerificationRequestOut:
        request = self.profile_repo.get_verification_request_by_id(request_id)

        if request is None:
            raise ValidationAuthError(
                message="Verification request not found",
                details={"request_id": request_id},
            )

        return self._verification_out(request)

    def update_verification_status(
        self,
        *,
        request_id: int,
        status: str,
        note: str | None,
        reviewer: AuthUser,
    ) -> AdminVerificationRequestOut:
        self._validate_admin_target_status(status)

        request = self.profile_repo.get_verification_request_by_id(request_id)

        if request is None:
            raise ValidationAuthError(
                message="Verification request not found",
                details={"request_id": request_id},
            )

        self._ensure_request_can_be_changed(request)

        if status == VerificationStatus.APPROVED.value:
            self._ensure_request_can_be_approved(request)

        now = datetime.utcnow()

        request.status = status
        request.admin_note = note
        request.reviewed_at = now
        request.reviewed_by = reviewer.id

        self.profile_repo.create_verification_review(
            request_id=request.id,
            reviewer_id=reviewer.id,
            action=status,
            note=note,
        )

        if status == VerificationStatus.APPROVED.value:
            self._assign_target_role(request, assigned_by=reviewer.id)

        self.profile_repo.commit()
        self.profile_repo.refresh(request)

        return self._verification_out(request)

    def _assign_target_role(
        self,
        request: VerificationRequest,
        *,
        assigned_by: int | None,
    ) -> None:
        role_code = request.target_role

        role = self.auth_repo.get_role_by_code(role_code)
        if role is None:
            raise ValidationAuthError(
                message="Target role is not seeded",
                details={"target_role": role_code},
            )

        self.auth_repo.assign_role_to_user(
            user_id=request.user_id,
            role_id=role.id,
            assigned_by=assigned_by,
        )

    def _ensure_request_can_be_changed(self, request: VerificationRequest) -> None:
        locked_statuses = {
            VerificationStatus.APPROVED.value,
            VerificationStatus.REJECTED.value,
            VerificationStatus.CANCELLED.value,
        }

        if request.status in locked_statuses:
            raise ValidationAuthError(
                message="Verification request status cannot be changed",
                details={
                    "request_id": request.id,
                    "current_status": request.status,
                },
            )

    def _ensure_request_can_be_approved(self, request: VerificationRequest) -> None:
        if not request.documents:
            raise ValidationAuthError(
                message="At least one document is required before approval",
                details={"request_id": request.id},
            )

        active_documents = [
            link
            for link in request.documents
            if link.document.deleted_at is None
        ]

        if not active_documents:
            raise ValidationAuthError(
                message="At least one active document is required before approval",
                details={"request_id": request.id},
            )

    def _validate_admin_target_status(self, status: str) -> None:
        allowed = {
            VerificationStatus.UNDER_REVIEW.value,
            VerificationStatus.NEEDS_REVISION.value,
            VerificationStatus.APPROVED.value,
            VerificationStatus.REJECTED.value,
        }

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid verification status",
                details={"allowed": sorted(allowed)},
            )

    def _validate_status_for_filter(self, status: str) -> None:
        allowed = {item.value for item in VerificationStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid verification status filter",
                details={"allowed": sorted(allowed)},
            )

    def _validate_target_role(self, target_role: str) -> None:
        allowed = {item.value for item in VerificationTargetRole}

        if target_role not in allowed:
            raise ValidationAuthError(
                message="Invalid target_role filter",
                details={"allowed": sorted(allowed)},
            )

    def _verification_out(self, request: VerificationRequest) -> AdminVerificationRequestOut:
        user = self.auth_repo.get_user_by_id(request.user_id)

        return AdminVerificationRequestOut(
            id=request.id,
            user_id=request.user_id,
            user_email=user.email if user else None,
            user_phone=user.phone if user else None,
            target_role=request.target_role,
            status=request.status,
            request_note=request.request_note,
            admin_note=request.admin_note,
            submitted_at=request.submitted_at,
            reviewed_at=request.reviewed_at,
            reviewed_by=request.reviewed_by,
            created_at=request.created_at,
            updated_at=request.updated_at,
            documents=[
                self._document_out(link)
                for link in request.documents
                if link.document.deleted_at is None
            ],
            reviews=[
                AdminVerificationReviewOut(
                    id=review.id,
                    reviewer_id=review.reviewer_id,
                    action=review.action,
                    note=review.note,
                    created_at=review.created_at,
                )
                for review in request.reviews
            ],
        )

    def _document_out(self, link) -> AdminVerificationDocumentOut:
        media = (
            self.profile_repo.get_media_by_id(media_file_id=link.document.media_file_id)
            if link.document.media_file_id
            else None
        )
        file_key = media.file_key if media else None

        return AdminVerificationDocumentOut(
            id=link.id,
            document_id=link.document.id,
            document_type=link.document.document_type,
            file_name=link.document.file_name,
            media_file_id=link.document.media_file_id,
            file_key=file_key,
            private_url=self._private_media_url(file_key=file_key),
            admin_private_url=self._admin_private_media_url(file_key=file_key),
            status=link.document.status,
        )

    def _private_media_url(self, *, file_key: str | None) -> str | None:
        if not file_key:
            return None
        return f"/api/v1/media/private/{file_key}"

    def _admin_private_media_url(self, *, file_key: str | None) -> str | None:
        if not file_key:
            return None
        return f"/api/v1/admin/media/private/{file_key}"
