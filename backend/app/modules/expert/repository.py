from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.expert.models import ExpertAnswer
from app.modules.social.models import SocialPost


class ExpertAnswerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, row: object) -> None:
        self.db.refresh(row)

    def add_answer(self, row: ExpertAnswer) -> ExpertAnswer:
        self.db.add(row)
        self.db.flush()
        return row

    def get_post_by_id(
        self,
        *,
        post_id: int,
    ) -> SocialPost | None:
        return self.db.query(SocialPost).filter(SocialPost.id == post_id).one_or_none()

    def get_published_post_by_id(
        self,
        *,
        post_id: int,
    ) -> SocialPost | None:
        return (
            self.db.query(SocialPost)
            .filter(
                SocialPost.id == post_id,
                SocialPost.status == "published",
                SocialPost.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def get_answer_by_id(
        self,
        *,
        answer_id: int,
    ) -> ExpertAnswer | None:
        return (
            self.db.query(ExpertAnswer)
            .filter(ExpertAnswer.id == answer_id)
            .one_or_none()
        )

    def get_published_answer_by_id(
        self,
        *,
        answer_id: int,
    ) -> ExpertAnswer | None:
        return (
            self.db.query(ExpertAnswer)
            .filter(
                ExpertAnswer.id == answer_id,
                ExpertAnswer.status == "published",
                ExpertAnswer.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_published_answers_for_post(
        self,
        *,
        post_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ExpertAnswer], int]:
        query = self.db.query(ExpertAnswer).filter(
            ExpertAnswer.post_id == post_id,
            ExpertAnswer.status == "published",
            ExpertAnswer.deleted_at.is_(None),
        )

        total = query.count()

        rows = (
            query.order_by(
                ExpertAnswer.is_accepted.desc(),
                ExpertAnswer.created_at.desc(),
                ExpertAnswer.id.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def list_my_answers(
        self,
        *,
        expert_user_id: int,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ExpertAnswer], int]:
        query = self.db.query(ExpertAnswer).filter(
            ExpertAnswer.expert_user_id == expert_user_id
        )

        if status:
            query = query.filter(ExpertAnswer.status == status)

        total = query.count()

        rows = (
            query.order_by(ExpertAnswer.created_at.desc(), ExpertAnswer.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def list_admin_answers(
        self,
        *,
        status: str | None = None,
        post_id: int | None = None,
        expert_user_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ExpertAnswer], int]:
        query = self.db.query(ExpertAnswer)

        if status:
            query = query.filter(ExpertAnswer.status == status)

        if post_id:
            query = query.filter(ExpertAnswer.post_id == post_id)

        if expert_user_id:
            query = query.filter(ExpertAnswer.expert_user_id == expert_user_id)

        total = query.count()

        rows = (
            query.order_by(ExpertAnswer.created_at.desc(), ExpertAnswer.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total
