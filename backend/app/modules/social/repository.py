from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.modules.social.models import (
    SocialBookmark,
    SocialCategory,
    SocialComment,
    SocialModerationAction,
    SocialPost,
    SocialReaction,
)


class SocialRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, row: object) -> None:
        self.db.refresh(row)

    def add_category(self, row: SocialCategory) -> SocialCategory:
        self.db.add(row)
        self.db.flush()
        return row

    def get_category_by_code(self, *, code: str) -> SocialCategory | None:
        return (
            self.db.query(SocialCategory)
            .filter(SocialCategory.code == code)
            .one_or_none()
        )

    def get_category_by_id(self, *, category_id: int) -> SocialCategory | None:
        return (
            self.db.query(SocialCategory)
            .filter(SocialCategory.id == category_id)
            .one_or_none()
        )

    def list_active_categories(self) -> list[SocialCategory]:
        return (
            self.db.query(SocialCategory)
            .filter(SocialCategory.is_active == True)  # noqa: E712
            .order_by(SocialCategory.sort_order.asc(), SocialCategory.id.asc())
            .all()
        )

    def add_post(self, row: SocialPost) -> SocialPost:
        self.db.add(row)
        self.db.flush()
        return row

    def add_comment(self, row: SocialComment) -> SocialComment:
        self.db.add(row)
        self.db.flush()
        return row

    def add_reaction(self, row: SocialReaction) -> SocialReaction:
        self.db.add(row)
        self.db.flush()
        return row

    def delete_reaction(self, row: SocialReaction) -> None:
        self.db.delete(row)
        self.db.flush()

    def add_bookmark(self, row: SocialBookmark) -> SocialBookmark:
        self.db.add(row)
        self.db.flush()
        return row

    def delete_bookmark(self, row: SocialBookmark) -> None:
        self.db.delete(row)
        self.db.flush()

    def get_post_by_id(self, *, post_id: int) -> SocialPost | None:
        return self.db.query(SocialPost).filter(SocialPost.id == post_id).one_or_none()

    def get_published_post_by_id(self, *, post_id: int) -> SocialPost | None:
        return (
            self.db.query(SocialPost)
            .filter(
                SocialPost.id == post_id,
                SocialPost.status == "published",
            )
            .one_or_none()
        )

    def get_comment_by_id(
        self,
        *,
        comment_id: int,
    ) -> SocialComment | None:
        return (
            self.db.query(SocialComment)
            .filter(SocialComment.id == comment_id)
            .one_or_none()
        )

    def get_published_comment_by_id(
        self,
        *,
        comment_id: int,
    ) -> SocialComment | None:
        return (
            self.db.query(SocialComment)
            .filter(
                SocialComment.id == comment_id,
                SocialComment.status == "published",
            )
            .one_or_none()
        )

    def get_post_reaction(
        self,
        *,
        post_id: int,
        user_id: int,
        reaction_type: str,
    ) -> SocialReaction | None:
        return (
            self.db.query(SocialReaction)
            .filter(
                SocialReaction.post_id == post_id,
                SocialReaction.comment_id.is_(None),
                SocialReaction.user_id == user_id,
                SocialReaction.reaction_type == reaction_type,
            )
            .one_or_none()
        )

    def get_comment_reaction(
        self,
        *,
        comment_id: int,
        user_id: int,
        reaction_type: str,
    ) -> SocialReaction | None:
        return (
            self.db.query(SocialReaction)
            .filter(
                SocialReaction.post_id.is_(None),
                SocialReaction.comment_id == comment_id,
                SocialReaction.user_id == user_id,
                SocialReaction.reaction_type == reaction_type,
            )
            .one_or_none()
        )

    def get_bookmark(
        self,
        *,
        post_id: int,
        user_id: int,
    ) -> SocialBookmark | None:
        return (
            self.db.query(SocialBookmark)
            .filter(
                SocialBookmark.post_id == post_id,
                SocialBookmark.user_id == user_id,
            )
            .one_or_none()
        )

    def list_published_posts(
        self,
        *,
        category_id: int | None = None,
        post_type: str | None = None,
        q: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SocialPost], int]:
        query = self.db.query(SocialPost).filter(
            SocialPost.status == "published",
            SocialPost.visibility == "public",
        )

        if category_id is not None:
            query = query.filter(SocialPost.category_id == category_id)

        if post_type is not None:
            query = query.filter(SocialPost.post_type == post_type)

        if q:
            like = f"%{q}%"
            query = query.filter(
                or_(
                    SocialPost.title.like(like),
                    SocialPost.body.like(like),
                )
            )

        total = query.count()

        rows = (
            query.order_by(SocialPost.published_at.desc(), SocialPost.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def list_user_posts(
        self,
        *,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SocialPost], int]:
        query = self.db.query(SocialPost).filter(
            SocialPost.author_user_id == user_id,
            SocialPost.status != "deleted",
        )

        total = query.count()

        rows = (
            query.order_by(SocialPost.created_at.desc(), SocialPost.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def list_post_comments(
        self,
        *,
        post_id: int,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[SocialComment], int]:
        query = self.db.query(SocialComment).filter(
            SocialComment.post_id == post_id,
            SocialComment.status == "published",
        )

        total = query.count()

        rows = (
            query.order_by(
                SocialComment.parent_comment_id.asc(),
                SocialComment.created_at.asc(),
                SocialComment.id.asc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def list_user_bookmarks(
        self,
        *,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[tuple[SocialBookmark, SocialPost]], int]:
        query = (
            self.db.query(SocialBookmark, SocialPost)
            .join(SocialPost, SocialPost.id == SocialBookmark.post_id)
            .filter(
                SocialBookmark.user_id == user_id,
                SocialPost.status == "published",
                SocialPost.visibility == "public",
            )
        )

        total = query.count()

        rows = (
            query.order_by(SocialBookmark.created_at.desc(), SocialBookmark.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def add_moderation_action(
        self,
        row: SocialModerationAction,
    ) -> SocialModerationAction:
        self.db.add(row)
        self.db.flush()
        return row

    def now(self) -> datetime:
        return datetime.utcnow()
