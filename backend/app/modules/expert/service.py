from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.consultants.enums import ConsultProfileStatus
from app.modules.consultants.repository import ConsultantRepository
from app.modules.expert.enums import ExpertAnswerStatus
from app.modules.expert.models import ExpertAnswer
from app.modules.expert.repository import ExpertAnswerRepository
from app.modules.expert.schemas import (
    ExpertAnswerAdminOut,
    ExpertAnswerConsultantOut,
    ExpertAnswerConsultantSpecialtyOut,
    ExpertAnswerCreateIn,
    ExpertAnswerModerationIn,
    ExpertAnswerOut,
    ExpertAnswerPostPreviewOut,
    ExpertAnswerPublicOut,
    ExpertAnswerStatusUpdateIn,
)
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.schemas import NotificationEventCreateIn
from app.modules.notifications.service import NotificationService
from app.modules.social.models import SocialPost


class ExpertAnswerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ExpertAnswerRepository(db)
        self.consultant_repo = ConsultantRepository(db)

    def create_answer(
        self,
        *,
        post_id: int,
        expert_user_id: int,
        payload: ExpertAnswerCreateIn,
    ) -> ExpertAnswerOut:
        post = self.repo.get_published_post_by_id(post_id=post_id)

        if post is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        row = ExpertAnswer(
            post_id=post_id,
            expert_user_id=expert_user_id,
            body=payload.body.strip(),
            status=ExpertAnswerStatus.PUBLISHED.value,
            is_accepted=False,
            accepted_at=None,
            accepted_by_user_id=None,
            helpful_count=0,
            reports_count=0,
            deleted_at=None,
        )

        self.repo.add_answer(row)
        self._notify_post_owner_about_answer(
            post=post,
            answer=row,
            expert_user_id=expert_user_id,
        )
        self.repo.commit()
        self.repo.refresh(row)

        return ExpertAnswerOut.model_validate(row)

    def list_published_answers_for_post(
        self,
        *,
        post_id: int,
        page: int,
        page_size: int,
    ) -> tuple[list[ExpertAnswerPublicOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        post = self.repo.get_published_post_by_id(post_id=post_id)

        if post is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        rows, total = self.repo.list_published_answers_for_post(
            post_id=post_id,
            page=page,
            page_size=page_size,
        )

        return [self._public_answer_out(row) for row in rows], total

    def list_my_answers(
        self,
        *,
        expert_user_id: int,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ExpertAnswerOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_status(status)

        rows, total = self.repo.list_my_answers(
            expert_user_id=expert_user_id,
            status=status,
            page=page,
            page_size=page_size,
        )

        return [ExpertAnswerOut.model_validate(row) for row in rows], total

    def soft_delete_own_answer(
        self,
        *,
        answer_id: int,
        expert_user_id: int,
    ) -> ExpertAnswerOut:
        row = self.repo.get_answer_by_id(answer_id=answer_id)

        if row is None or row.expert_user_id != expert_user_id:
            raise ValidationAuthError(
                message="Expert answer not found",
                details={"answer_id": answer_id},
            )

        row.status = ExpertAnswerStatus.DELETED.value
        row.deleted_at = datetime.utcnow()

        self.repo.commit()
        self.repo.refresh(row)

        return ExpertAnswerOut.model_validate(row)

    def list_admin_answers(
        self,
        *,
        status: str | None,
        post_id: int | None,
        expert_user_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ExpertAnswerAdminOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_admin_list_status(status)

        rows, total = self.repo.list_admin_answers(
            status=status,
            post_id=post_id,
            expert_user_id=expert_user_id,
            page=page,
            page_size=page_size,
        )

        return [self._admin_answer_out(row) for row in rows], total

    def update_answer_status_admin(
        self,
        *,
        answer_id: int,
        admin_user_id: int,
        payload: ExpertAnswerStatusUpdateIn,
    ) -> ExpertAnswerAdminOut:
        _ = admin_user_id
        self._validate_admin_status_update(payload.status)

        row = self.repo.get_answer_by_id(answer_id=answer_id)

        if row is None:
            raise ValidationAuthError(
                message="Expert answer not found",
                details={"answer_id": answer_id},
            )

        row.status = payload.status
        row.deleted_at = None

        self.repo.commit()
        self.repo.refresh(row)

        return self._admin_answer_out(row)

    def soft_delete_answer_admin(
        self,
        *,
        answer_id: int,
        admin_user_id: int,
    ) -> ExpertAnswerAdminOut:
        _ = admin_user_id

        row = self.repo.get_answer_by_id(answer_id=answer_id)

        if row is None:
            raise ValidationAuthError(
                message="Expert answer not found",
                details={"answer_id": answer_id},
            )

        row.status = ExpertAnswerStatus.DELETED.value
        row.deleted_at = datetime.utcnow()

        self.repo.commit()
        self.repo.refresh(row)

        return self._admin_answer_out(row)

    def hide_answer_admin(
        self,
        *,
        answer_id: int,
        moderator_user_id: int,
        payload: ExpertAnswerModerationIn,
    ) -> ExpertAnswerOut:
        _ = moderator_user_id
        _ = payload

        row = self.repo.get_answer_by_id(answer_id=answer_id)

        if row is None:
            raise ValidationAuthError(
                message="Expert answer not found",
                details={"answer_id": answer_id},
            )

        row.status = ExpertAnswerStatus.HIDDEN.value

        self.repo.commit()
        self.repo.refresh(row)

        return ExpertAnswerOut.model_validate(row)

    def unhide_answer_admin(
        self,
        *,
        answer_id: int,
        moderator_user_id: int,
        payload: ExpertAnswerModerationIn,
    ) -> ExpertAnswerOut:
        _ = moderator_user_id
        _ = payload

        row = self.repo.get_answer_by_id(answer_id=answer_id)

        if row is None:
            raise ValidationAuthError(
                message="Expert answer not found",
                details={"answer_id": answer_id},
            )

        row.status = ExpertAnswerStatus.PUBLISHED.value
        row.deleted_at = None

        self.repo.commit()
        self.repo.refresh(row)

        return ExpertAnswerOut.model_validate(row)

    def _validate_status(self, status: str) -> None:
        allowed = {item.value for item in ExpertAnswerStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid expert answer status",
                details={"allowed": sorted(allowed)},
            )

    def _notify_post_owner_about_answer(
        self,
        *,
        post: SocialPost,
        answer: ExpertAnswer,
        expert_user_id: int,
    ) -> None:
        if answer.status != ExpertAnswerStatus.PUBLISHED.value:
            return

        if post.author_user_id == expert_user_id:
            return

        event_key = f"expert_answer_created:expert_answer:{answer.id}"
        notification_service = NotificationService(self.db)

        if notification_service.repo.get_event_by_key(event_key=event_key) is not None:
            return

        event = notification_service.create_event(
            payload=NotificationEventCreateIn(
                event_key=event_key,
                event_type=NotificationEventType.EXPERT_ANSWER_CREATED.value,
                actor_user_id=expert_user_id,
                source_type="expert_answer",
                source_id=str(answer.id),
                payload_json={
                    "answer_id": answer.id,
                    "post_id": post.id,
                    "expert_user_id": expert_user_id,
                },
            ),
            commit=False,
        )

        notification_service.notify_user(
            recipient_user_id=post.author_user_id,
            title="پاسخ تخصصی جدید برای پست شما",
            body=f"برای پست «{post.title}» یک پاسخ تخصصی ثبت شد.",
            event_id=event.id,
            action_url=f"/social/posts/{post.id}",
            priority="normal",
            commit=False,
        )

    def _validate_admin_list_status(self, status: str) -> None:
        allowed = {
            ExpertAnswerStatus.PUBLISHED.value,
            ExpertAnswerStatus.HIDDEN.value,
            ExpertAnswerStatus.DELETED.value,
        }

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid expert answer status",
                details={"allowed": sorted(allowed)},
            )

    def _validate_admin_status_update(self, status: str) -> None:
        allowed = {
            ExpertAnswerStatus.PUBLISHED.value,
            ExpertAnswerStatus.HIDDEN.value,
        }

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid expert answer status",
                details={"allowed": sorted(allowed)},
            )

    def _public_answer_out(self, row: ExpertAnswer) -> ExpertAnswerPublicOut:
        data = ExpertAnswerOut.model_validate(row).model_dump()
        return ExpertAnswerPublicOut(
            **data,
            answer_id=row.id,
            expert_id=row.expert_user_id,
            consultant=self._consultant_out(
                expert_user_id=row.expert_user_id,
                public_only=True,
            ),
        )

    def _admin_answer_out(self, row: ExpertAnswer) -> ExpertAnswerAdminOut:
        return ExpertAnswerAdminOut(
            answer_id=row.id,
            post_id=row.post_id,
            expert_id=row.expert_user_id,
            expert_user_id=row.expert_user_id,
            body=row.body,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
            post_title=row.post.title if row.post is not None else None,
            consultant=self._consultant_out(
                expert_user_id=row.expert_user_id,
                public_only=False,
            ),
            post_preview=self._post_preview_out(row.post),
        )

    def _consultant_out(
        self,
        *,
        expert_user_id: int,
        public_only: bool,
    ) -> ExpertAnswerConsultantOut | None:
        profile = self.consultant_repo.get_profile_by_user_id(expert_user_id)

        if profile is None:
            return None

        if public_only and profile.status != ConsultProfileStatus.APPROVED.value:
            return None

        avatar_url = None
        if profile.avatar_media_file_id:
            media = self.consultant_repo.get_media_file_by_id(profile.avatar_media_file_id)
            if media is not None and media.file_key:
                avatar_url = f"/api/v1/media/public/{media.file_key}"

        specialties = []
        for link in profile.specialty_links:
            specialty = link.specialty
            if specialty is None:
                continue
            if public_only and not specialty.is_active:
                continue
            specialties.append(
                ExpertAnswerConsultantSpecialtyOut(
                    id=specialty.id,
                    code=specialty.code,
                    title=specialty.title,
                )
            )

        display_name = profile.display_name

        return ExpertAnswerConsultantOut(
            consultant_id=profile.id,
            user_id=profile.user_id,
            display_name=display_name,
            name=display_name,
            title=profile.title,
            avatar_file_id=profile.avatar_file_id,
            avatar_media_file_id=profile.avatar_media_file_id,
            avatar_url=avatar_url,
            status=profile.status,
            is_verified=profile.status == ConsultProfileStatus.APPROVED.value,
            verification_status=profile.status,
            is_featured=profile.is_featured,
            rating_average=profile.rating_average or Decimal("0.00"),
            reviews_count=profile.reviews_count,
            specialties=specialties,
        )

    def _post_preview_out(
        self,
        row: SocialPost | None,
    ) -> ExpertAnswerPostPreviewOut | None:
        if row is None:
            return None

        return ExpertAnswerPostPreviewOut(
            id=row.id,
            author_user_id=row.author_user_id,
            title=row.title,
            post_type=row.post_type,
            status=row.status,
            created_at=row.created_at,
        )
