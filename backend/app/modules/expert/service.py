from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.expert.enums import ExpertAnswerStatus
from app.modules.expert.models import ExpertAnswer
from app.modules.expert.repository import ExpertAnswerRepository
from app.modules.expert.schemas import (
    ExpertAnswerCreateIn,
    ExpertAnswerModerationIn,
    ExpertAnswerOut,
)


class ExpertAnswerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ExpertAnswerRepository(db)

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
        self.repo.commit()
        self.repo.refresh(row)

        return ExpertAnswerOut.model_validate(row)

    def list_published_answers_for_post(
        self,
        *,
        post_id: int,
        page: int,
        page_size: int,
    ) -> tuple[list[ExpertAnswerOut], int]:
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

        return [ExpertAnswerOut.model_validate(row) for row in rows], total

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
    ) -> tuple[list[ExpertAnswerOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_status(status)

        rows, total = self.repo.list_admin_answers(
            status=status,
            post_id=post_id,
            expert_user_id=expert_user_id,
            page=page,
            page_size=page_size,
        )

        return [ExpertAnswerOut.model_validate(row) for row in rows], total

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
