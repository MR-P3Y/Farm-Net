from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.social.enums import (
    SocialCommentStatus,
    SocialModerationActionType,
    SocialModerationTargetType,
    SocialPostStatus,
    SocialPostType,
    SocialPostVisibility,
)
from app.modules.social.models import (
    SocialCategory,
    SocialComment,
    SocialModerationAction,
    SocialPost,
)
from app.modules.social.repository import SocialRepository
from app.modules.social.schemas import (
    SocialCategoryOut,
    SocialCommentCreateIn,
    SocialCommentOut,
    SocialPostCreateIn,
    SocialPostListFilter,
    SocialPostModerationIn,
    SocialPostOut,
)


class SocialService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SocialRepository(db)

    def seed_default_categories(self) -> list[SocialCategoryOut]:
        defaults = [
            {
                "code": "general",
                "title": "عمومی",
                "description": "گفتگوها و موضوعات عمومی کشاورزی",
                "sort_order": 100,
            },
            {
                "code": "questions",
                "title": "پرسش و پاسخ",
                "description": "سؤال‌های کاربران و پاسخ جامعه",
                "sort_order": 200,
            },
            {
                "code": "experiences",
                "title": "تجربه‌ها",
                "description": "تجربه‌های واقعی کشاورزان و فعالان حوزه کشاورزی",
                "sort_order": 300,
            },
            {
                "code": "problems",
                "title": "مشکلات، آفت و بیماری",
                "description": "طرح مشکل محصول، آفت، بیماری یا کمبود",
                "sort_order": 400,
            },
            {
                "code": "education",
                "title": "آموزش و راهنما",
                "description": "محتوای آموزشی و راهنماهای کاربردی",
                "sort_order": 500,
            },
            {
                "code": "market",
                "title": "بازار و خرید و فروش",
                "description": "بحث‌های مرتبط با بازار، قیمت و خرید و فروش مجاز",
                "sort_order": 600,
            },
        ]

        rows: list[SocialCategory] = []

        for item in defaults:
            row = self.repo.get_category_by_code(code=item["code"])

            if row is None:
                row = SocialCategory(
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

        return [SocialCategoryOut.model_validate(row) for row in rows]

    def list_categories(self) -> list[SocialCategoryOut]:
        rows = self.repo.list_active_categories()
        return [SocialCategoryOut.model_validate(row) for row in rows]

    def create_post(
        self,
        *,
        author_user_id: int,
        payload: SocialPostCreateIn,
    ) -> SocialPostOut:
        self._validate_post_type(payload.post_type)
        self._validate_visibility(payload.visibility)

        if payload.category_id is not None:
            category = self.repo.get_category_by_id(category_id=payload.category_id)

            if category is None or not category.is_active:
                raise ValidationAuthError(
                    message="Social category not found",
                    details={"category_id": payload.category_id},
                )

        now = datetime.utcnow()

        row = SocialPost(
            author_user_id=author_user_id,
            category_id=payload.category_id,
            title=payload.title.strip(),
            body=payload.body.strip(),
            post_type=payload.post_type,
            status=SocialPostStatus.PUBLISHED.value,
            visibility=payload.visibility,
            media_file_id=payload.media_file_id,
            country_code=payload.country_code.upper() if payload.country_code else None,
            province_id=payload.province_id,
            city_id=payload.city_id,
            village_id=payload.village_id,
            province_name=payload.province_name,
            city_name=payload.city_name,
            village_name=payload.village_name,
            latitude=payload.latitude,
            longitude=payload.longitude,
            views_count=0,
            comments_count=0,
            reactions_count=0,
            reports_count=0,
            metadata_json=payload.metadata_json,
            published_at=now,
            deleted_at=None,
        )

        self.repo.add_post(row)
        self.repo.commit()
        self.repo.refresh(row)

        return SocialPostOut.model_validate(row)

    def list_published_posts(
        self,
        *,
        filters: SocialPostListFilter,
    ) -> tuple[list[SocialPostOut], int]:
        page = max(filters.page, 1)
        page_size = min(max(filters.page_size, 1), 100)

        if filters.post_type is not None:
            self._validate_post_type(filters.post_type)

        if filters.category_id is not None:
            category = self.repo.get_category_by_id(category_id=filters.category_id)

            if category is None or not category.is_active:
                raise ValidationAuthError(
                    message="Social category not found",
                    details={"category_id": filters.category_id},
                )

        rows, total = self.repo.list_published_posts(
            category_id=filters.category_id,
            post_type=filters.post_type,
            q=filters.q,
            page=page,
            page_size=page_size,
        )

        return [SocialPostOut.model_validate(row) for row in rows], total

    def get_published_post(
        self,
        *,
        post_id: int,
    ) -> SocialPostOut:
        row = self.repo.get_published_post_by_id(post_id=post_id)

        if row is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        row.views_count += 1
        self.repo.commit()
        self.repo.refresh(row)

        return SocialPostOut.model_validate(row)

    def list_my_posts(
        self,
        *,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SocialPostOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        rows, total = self.repo.list_user_posts(
            user_id=user_id,
            page=page,
            page_size=page_size,
        )

        return [SocialPostOut.model_validate(row) for row in rows], total

    def create_comment(
        self,
        *,
        author_user_id: int,
        post_id: int,
        payload: SocialCommentCreateIn,
    ) -> SocialCommentOut:
        post = self.repo.get_published_post_by_id(post_id=post_id)

        if post is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        parent_comment_id = payload.parent_comment_id

        if parent_comment_id is not None:
            parent = self.repo.get_published_comment_by_id(
                comment_id=parent_comment_id,
            )

            if parent is None or parent.post_id != post_id:
                raise ValidationAuthError(
                    message="Parent comment not found",
                    details={"parent_comment_id": parent_comment_id},
                )

            if parent.parent_comment_id is not None:
                raise ValidationAuthError(
                    message="Nested replies are not allowed",
                    details={"parent_comment_id": parent_comment_id},
                )

        row = SocialComment(
            post_id=post_id,
            author_user_id=author_user_id,
            parent_comment_id=parent_comment_id,
            body=payload.body.strip(),
            status=SocialCommentStatus.PUBLISHED.value,
            reactions_count=0,
            reports_count=0,
            deleted_at=None,
        )

        self.repo.add_comment(row)

        post.comments_count += 1

        self.repo.commit()
        self.repo.refresh(row)

        return SocialCommentOut.model_validate(row)

    def list_post_comments(
        self,
        *,
        post_id: int,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[SocialCommentOut], int]:
        post = self.repo.get_published_post_by_id(post_id=post_id)

        if post is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        rows, total = self.repo.list_post_comments(
            post_id=post_id,
            page=page,
            page_size=page_size,
        )

        return [SocialCommentOut.model_validate(row) for row in rows], total

    def soft_delete_own_comment(
        self,
        *,
        user_id: int,
        comment_id: int,
    ) -> SocialCommentOut:
        row = self.repo.get_comment_by_id(comment_id=comment_id)

        if row is None or row.author_user_id != user_id:
            raise ValidationAuthError(
                message="Social comment not found",
                details={"comment_id": comment_id},
            )

        if row.status != SocialCommentStatus.DELETED.value:
            post = self.repo.get_post_by_id(post_id=row.post_id)
            if post is not None and post.comments_count > 0:
                post.comments_count -= 1

        row.status = SocialCommentStatus.DELETED.value
        row.deleted_at = datetime.utcnow()

        self.repo.commit()
        self.repo.refresh(row)

        return SocialCommentOut.model_validate(row)

    def soft_delete_own_post(
        self,
        *,
        user_id: int,
        post_id: int,
    ) -> SocialPostOut:
        row = self.repo.get_post_by_id(post_id=post_id)

        if row is None or row.author_user_id != user_id:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        row.status = SocialPostStatus.DELETED.value
        row.deleted_at = datetime.utcnow()

        self.repo.commit()
        self.repo.refresh(row)

        return SocialPostOut.model_validate(row)

    def hide_post_admin(
        self,
        *,
        moderator_user_id: int,
        post_id: int,
        payload: SocialPostModerationIn,
    ) -> SocialPostOut:
        row = self.repo.get_post_by_id(post_id=post_id)

        if row is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        row.status = SocialPostStatus.HIDDEN.value

        self.repo.add_moderation_action(
            SocialModerationAction(
                moderator_user_id=moderator_user_id,
                target_type=SocialModerationTargetType.POST.value,
                post_id=row.id,
                comment_id=None,
                action_type=SocialModerationActionType.HIDE.value,
                reason=payload.reason,
                metadata_json=None,
            )
        )

        self.repo.commit()
        self.repo.refresh(row)

        return SocialPostOut.model_validate(row)

    def unhide_post_admin(
        self,
        *,
        moderator_user_id: int,
        post_id: int,
        payload: SocialPostModerationIn,
    ) -> SocialPostOut:
        row = self.repo.get_post_by_id(post_id=post_id)

        if row is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        row.status = SocialPostStatus.PUBLISHED.value
        row.deleted_at = None

        self.repo.add_moderation_action(
            SocialModerationAction(
                moderator_user_id=moderator_user_id,
                target_type=SocialModerationTargetType.POST.value,
                post_id=row.id,
                comment_id=None,
                action_type=SocialModerationActionType.UNHIDE.value,
                reason=payload.reason,
                metadata_json=None,
            )
        )

        self.repo.commit()
        self.repo.refresh(row)

        return SocialPostOut.model_validate(row)

    def _validate_post_type(self, post_type: str) -> None:
        allowed = {item.value for item in SocialPostType}

        if post_type not in allowed:
            raise ValidationAuthError(
                message="Invalid social post type",
                details={"allowed": sorted(allowed)},
            )

    def _validate_visibility(self, visibility: str) -> None:
        allowed = {item.value for item in SocialPostVisibility}

        if visibility not in allowed:
            raise ValidationAuthError(
                message="Invalid social post visibility",
                details={"allowed": sorted(allowed)},
            )
