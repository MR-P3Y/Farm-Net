from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.expert.service import ExpertAnswerService
from app.modules.media.enums import MediaPurpose, MediaStatus, MediaVisibility
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.service import NotificationService
from app.modules.social.enums import (
    SocialCommentStatus,
    SocialModerationActionType,
    SocialModerationTargetType,
    SocialPostStatus,
    SocialPostType,
    SocialPostVisibility,
    SocialReactionType,
    SocialReportReason,
    SocialReportStatus,
    SocialReportTargetType,
)
from app.modules.social.models import (
    SocialBookmark,
    SocialCategory,
    SocialComment,
    SocialModerationAction,
    SocialPost,
    SocialReaction,
    SocialReport,
)
from app.modules.social.repository import SocialRepository
from app.modules.social.schemas import (
    SocialAdminCommentOut,
    SocialBookmarkOut,
    SocialBookmarkPostOut,
    SocialCategoryOut,
    SocialCategoryCreateIn,
    SocialCategoryUpdateIn,
    SocialCommentCreateIn,
    SocialCommentOut,
    SocialPostCreateIn,
    SocialPostDetailOut,
    SocialPostListFilter,
    SocialPostModerationIn,
    SocialPostOut,
    SocialReactionCreateIn,
    SocialReactionOut,
    SocialReportCreateIn,
    SocialReportOut,
    SocialReportStatusUpdateIn,
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
            rows.append(row)

        self.repo.commit()

        for row in rows:
            self.repo.refresh(row)

        return [self._category_out(row) for row in rows]

    def list_categories(self) -> list[SocialCategoryOut]:
        rows = self.repo.list_active_categories()
        return [self._category_out(row) for row in rows]

    def list_categories_admin(self, *, q: str | None = None) -> list[SocialCategoryOut]:
        return [self._category_out(row) for row in self.repo.list_categories_admin(q=q)]

    def create_category(self, payload: SocialCategoryCreateIn) -> SocialCategoryOut:
        row = SocialCategory(**payload.model_dump())
        self.repo.add_category(row)
        self._commit_category(code=payload.code)
        self.repo.refresh(row)
        return self._category_out(row)

    def update_category(self, *, category_id: int, payload: SocialCategoryUpdateIn) -> SocialCategoryOut:
        row = self.repo.get_category_by_id(category_id=category_id)
        if row is None:
            raise ValidationAuthError(message="Social category not found")
        changes = payload.model_dump(exclude_unset=True)
        if changes.get("code", row.code) is None or changes.get("title", row.title) is None:
            raise ValidationAuthError(message="Social category code and title are required")
        for key, value in changes.items():
            setattr(row, key, value)
        self._commit_category(code=row.code)
        self.repo.refresh(row)
        return self._category_out(row)

    def _commit_category(self, *, code: str) -> None:
        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ValidationAuthError(message="Social category code already exists", details={"code": code}) from exc

    def _category_out(self, row: SocialCategory) -> SocialCategoryOut:
        data = SocialCategoryOut.model_validate(row).model_dump()
        data["posts_count"] = self.repo.category_posts_count(category_id=row.id)
        return SocialCategoryOut.model_validate(data)

    def create_post(
        self,
        *,
        author_user_id: int,
        payload: SocialPostCreateIn,
    ) -> SocialPostOut:
        self._validate_post_type(payload.post_type)
        self._validate_visibility(payload.visibility)
        self._validate_social_post_media(
            media_file_id=payload.media_file_id,
            author_user_id=author_user_id,
        )

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

        return self._social_post_out(row)

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

        return [self._social_post_out(row) for row in rows], total

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

        return self._social_post_out(row)

    def get_published_post_detail(
        self,
        *,
        post_id: int,
    ) -> SocialPostDetailOut:
        row = self.repo.get_published_post_by_id(post_id=post_id)

        if row is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        row.views_count += 1
        self.repo.commit()
        self.repo.refresh(row)

        return self._social_post_detail_out(row)

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

        return [self._social_post_out(row) for row in rows], total

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
        parent: SocialComment | None = None

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

        if parent_comment_id is None:
            if post.author_user_id != author_user_id:
                self._notify_user(
                    recipient_user_id=post.author_user_id,
                    event_type=NotificationEventType.SOCIAL_COMMENT_CREATED.value,
                    title="کامنت جدید روی پست شما",
                    body=f"برای پست «{post.title}» یک کامنت جدید ثبت شد.",
                    source_type="social_post",
                    source_id=str(post.id),
                    payload_json={
                        "post_id": post.id,
                        "comment_id": row.id,
                        "actor_user_id": author_user_id,
                    },
                    action_url=f"/social/posts/{post.id}",
                )
        elif parent is not None and parent.author_user_id != author_user_id:
            self._notify_user(
                recipient_user_id=parent.author_user_id,
                event_type=NotificationEventType.SOCIAL_REPLY_CREATED.value,
                title="پاسخ جدید به کامنت شما",
                body=f"برای کامنت شما در پست «{post.title}» یک پاسخ ثبت شد.",
                source_type="social_comment",
                source_id=str(parent.id),
                payload_json={
                    "post_id": post.id,
                    "comment_id": row.id,
                    "parent_comment_id": parent.id,
                    "actor_user_id": author_user_id,
                },
                action_url=f"/social/posts/{post.id}",
            )

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

    def react_to_post(
        self,
        *,
        user_id: int,
        post_id: int,
        payload: SocialReactionCreateIn,
    ) -> tuple[SocialReactionOut, bool]:
        self._validate_reaction_type(payload.reaction_type)

        post = self.repo.get_published_post_by_id(post_id=post_id)

        if post is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        existing = self.repo.get_post_reaction(
            post_id=post_id,
            user_id=user_id,
            reaction_type=payload.reaction_type,
        )

        if existing is not None:
            return SocialReactionOut.model_validate(existing), False

        row = SocialReaction(
            post_id=post_id,
            comment_id=None,
            user_id=user_id,
            reaction_type=payload.reaction_type,
        )

        self.repo.add_reaction(row)
        post.reactions_count += 1

        self.repo.commit()
        self.repo.refresh(row)

        return SocialReactionOut.model_validate(row), True

    def remove_post_reaction(
        self,
        *,
        user_id: int,
        post_id: int,
        reaction_type: str,
    ) -> dict:
        self._validate_reaction_type(reaction_type)

        post = self.repo.get_published_post_by_id(post_id=post_id)

        if post is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        existing = self.repo.get_post_reaction(
            post_id=post_id,
            user_id=user_id,
            reaction_type=reaction_type,
        )

        if existing is None:
            return {
                "deleted": False,
                "post_id": post_id,
                "reaction_type": reaction_type,
            }

        self.repo.delete_reaction(existing)

        if post.reactions_count > 0:
            post.reactions_count -= 1

        self.repo.commit()

        return {
            "deleted": True,
            "post_id": post_id,
            "reaction_type": reaction_type,
        }

    def react_to_comment(
        self,
        *,
        user_id: int,
        comment_id: int,
        payload: SocialReactionCreateIn,
    ) -> tuple[SocialReactionOut, bool]:
        self._validate_reaction_type(payload.reaction_type)

        comment = self.repo.get_published_comment_by_id(comment_id=comment_id)

        if comment is None:
            raise ValidationAuthError(
                message="Social comment not found",
                details={"comment_id": comment_id},
            )

        post = self.repo.get_published_post_by_id(post_id=comment.post_id)

        if post is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": comment.post_id},
            )

        existing = self.repo.get_comment_reaction(
            comment_id=comment_id,
            user_id=user_id,
            reaction_type=payload.reaction_type,
        )

        if existing is not None:
            return SocialReactionOut.model_validate(existing), False

        row = SocialReaction(
            post_id=None,
            comment_id=comment_id,
            user_id=user_id,
            reaction_type=payload.reaction_type,
        )

        self.repo.add_reaction(row)
        comment.reactions_count += 1

        self.repo.commit()
        self.repo.refresh(row)

        return SocialReactionOut.model_validate(row), True

    def remove_comment_reaction(
        self,
        *,
        user_id: int,
        comment_id: int,
        reaction_type: str,
    ) -> dict:
        self._validate_reaction_type(reaction_type)

        comment = self.repo.get_published_comment_by_id(comment_id=comment_id)

        if comment is None:
            raise ValidationAuthError(
                message="Social comment not found",
                details={"comment_id": comment_id},
            )

        existing = self.repo.get_comment_reaction(
            comment_id=comment_id,
            user_id=user_id,
            reaction_type=reaction_type,
        )

        if existing is None:
            return {
                "deleted": False,
                "comment_id": comment_id,
                "reaction_type": reaction_type,
            }

        self.repo.delete_reaction(existing)

        if comment.reactions_count > 0:
            comment.reactions_count -= 1

        self.repo.commit()

        return {
            "deleted": True,
            "comment_id": comment_id,
            "reaction_type": reaction_type,
        }

    def bookmark_post(
        self,
        *,
        user_id: int,
        post_id: int,
    ) -> tuple[SocialBookmarkOut, bool]:
        post = self.repo.get_published_post_by_id(post_id=post_id)

        if post is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        existing = self.repo.get_bookmark(post_id=post_id, user_id=user_id)

        if existing is not None:
            return SocialBookmarkOut.model_validate(existing), False

        row = SocialBookmark(
            post_id=post_id,
            user_id=user_id,
        )

        self.repo.add_bookmark(row)
        self.repo.commit()
        self.repo.refresh(row)

        return SocialBookmarkOut.model_validate(row), True

    def remove_bookmark(
        self,
        *,
        user_id: int,
        post_id: int,
    ) -> dict:
        existing = self.repo.get_bookmark(post_id=post_id, user_id=user_id)

        if existing is None:
            return {
                "deleted": False,
                "post_id": post_id,
            }

        self.repo.delete_bookmark(existing)
        self.repo.commit()

        return {
            "deleted": True,
            "post_id": post_id,
        }

    def list_my_bookmarks(
        self,
        *,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SocialBookmarkPostOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        rows, total = self.repo.list_user_bookmarks(
            user_id=user_id,
            page=page,
            page_size=page_size,
        )

        items = [
            SocialBookmarkPostOut(
                bookmark_id=bookmark.id,
                bookmarked_at=bookmark.created_at,
                post=self._social_post_out(post),
            )
            for bookmark, post in rows
        ]

        return items, total

    def report_post(
        self,
        *,
        reporter_user_id: int,
        post_id: int,
        payload: SocialReportCreateIn,
    ) -> SocialReportOut:
        self._validate_report_reason(payload.reason)

        post = self.repo.get_published_post_by_id(post_id=post_id)

        if post is None:
            raise ValidationAuthError(
                message="Social post not found",
                details={"post_id": post_id},
            )

        row = SocialReport(
            reporter_user_id=reporter_user_id,
            target_type=SocialReportTargetType.POST.value,
            post_id=post_id,
            comment_id=None,
            reason=payload.reason,
            description=payload.description,
            status=SocialReportStatus.OPEN.value,
            reviewed_by_user_id=None,
            reviewed_at=None,
        )

        self.repo.add_report(row)
        post.reports_count += 1

        self._notify_social_admins(
            event_type=NotificationEventType.SOCIAL_POST_REPORTED.value,
            title="گزارش جدید برای پست اجتماعی",
            body=f"پست «{post.title}» با دلیل «{payload.reason}» گزارش شد.",
            source_type="social_report",
            source_id=str(row.id),
            payload_json={
                "report_id": row.id,
                "post_id": post.id,
                "reason": payload.reason,
                "reporter_user_id": reporter_user_id,
            },
            action_url="/admin/social/reports",
            priority="high",
        )

        self.repo.commit()
        self.repo.refresh(row)

        return SocialReportOut.model_validate(row)

    def report_comment(
        self,
        *,
        reporter_user_id: int,
        comment_id: int,
        payload: SocialReportCreateIn,
    ) -> SocialReportOut:
        self._validate_report_reason(payload.reason)

        comment = self.repo.get_published_comment_by_id(comment_id=comment_id)

        if comment is None:
            raise ValidationAuthError(
                message="Social comment not found",
                details={"comment_id": comment_id},
            )

        row = SocialReport(
            reporter_user_id=reporter_user_id,
            target_type=SocialReportTargetType.COMMENT.value,
            post_id=None,
            comment_id=comment_id,
            reason=payload.reason,
            description=payload.description,
            status=SocialReportStatus.OPEN.value,
            reviewed_by_user_id=None,
            reviewed_at=None,
        )

        self.repo.add_report(row)
        comment.reports_count += 1

        self._notify_social_admins(
            event_type=NotificationEventType.SOCIAL_COMMENT_REPORTED.value,
            title="گزارش جدید برای کامنت اجتماعی",
            body=f"یک کامنت با دلیل «{payload.reason}» گزارش شد.",
            source_type="social_report",
            source_id=str(row.id),
            payload_json={
                "report_id": row.id,
                "comment_id": comment.id,
                "post_id": comment.post_id,
                "reason": payload.reason,
                "reporter_user_id": reporter_user_id,
            },
            action_url="/admin/social/reports",
            priority="high",
        )

        self.repo.commit()
        self.repo.refresh(row)

        return SocialReportOut.model_validate(row)

    def list_reports_admin(
        self,
        *,
        target_type: str | None,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[SocialReportOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if target_type is not None:
            self._validate_report_target_type(target_type)

        if status is not None:
            self._validate_report_status(status)

        rows, total = self.repo.list_reports(
            target_type=target_type,
            status=status,
            page=page,
            page_size=page_size,
        )

        return [SocialReportOut.model_validate(row) for row in rows], total

    def update_report_status_admin(
        self,
        *,
        admin_user_id: int,
        report_id: int,
        payload: SocialReportStatusUpdateIn,
    ) -> SocialReportOut:
        self._validate_report_status(payload.status)

        row = self.repo.get_report_by_id(report_id=report_id)

        if row is None:
            raise ValidationAuthError(
                message="Social report not found",
                details={"report_id": report_id},
            )

        row.status = payload.status
        row.reviewed_by_user_id = admin_user_id
        row.reviewed_at = datetime.utcnow()

        self.repo.commit()
        self.repo.refresh(row)

        return SocialReportOut.model_validate(row)

    def list_admin_posts(
        self,
        *,
        status: str | None,
        post_type: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[SocialPostOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_post_status(status)

        if post_type is not None:
            self._validate_post_type(post_type)

        rows, total = self.repo.list_admin_posts(
            status=status,
            post_type=post_type,
            page=page,
            page_size=page_size,
        )

        return [self._social_post_out(row) for row in rows], total

    def list_admin_comments(
        self,
        *,
        status: str | None,
        post_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[SocialAdminCommentOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_comment_status(status)

        rows, total = self.repo.list_admin_comments(
            status=status,
            post_id=post_id,
            page=page,
            page_size=page_size,
        )

        return [SocialAdminCommentOut.model_validate(row) for row in rows], total

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

        return self._social_post_out(row)

    def hide_comment_admin(
        self,
        *,
        moderator_user_id: int,
        comment_id: int,
        payload: SocialPostModerationIn,
    ) -> SocialAdminCommentOut:
        row = self.repo.get_comment_by_id(comment_id=comment_id)

        if row is None:
            raise ValidationAuthError(
                message="Social comment not found",
                details={"comment_id": comment_id},
            )

        row.status = SocialCommentStatus.HIDDEN.value

        self.repo.add_moderation_action(
            SocialModerationAction(
                moderator_user_id=moderator_user_id,
                target_type=SocialModerationTargetType.COMMENT.value,
                post_id=None,
                comment_id=row.id,
                action_type=SocialModerationActionType.HIDE.value,
                reason=payload.reason,
                metadata_json=None,
            )
        )

        if row.author_user_id != moderator_user_id:
            self._notify_user(
                recipient_user_id=row.author_user_id,
                event_type=NotificationEventType.SOCIAL_COMMENT_HIDDEN.value,
                title="کامنت شما مخفی شد",
                body="یکی از کامنت‌های شما توسط تیم مدیریت مخفی شد.",
                source_type="social_comment",
                source_id=str(row.id),
                payload_json={
                    "comment_id": row.id,
                    "post_id": row.post_id,
                    "moderator_user_id": moderator_user_id,
                    "reason": payload.reason,
                },
                action_url=f"/social/posts/{row.post_id}",
                priority="high",
            )

        self.repo.commit()
        self.repo.refresh(row)

        return SocialAdminCommentOut.model_validate(row)

    def unhide_comment_admin(
        self,
        *,
        moderator_user_id: int,
        comment_id: int,
        payload: SocialPostModerationIn,
    ) -> SocialAdminCommentOut:
        row = self.repo.get_comment_by_id(comment_id=comment_id)

        if row is None:
            raise ValidationAuthError(
                message="Social comment not found",
                details={"comment_id": comment_id},
            )

        row.status = SocialCommentStatus.PUBLISHED.value
        row.deleted_at = None

        self.repo.add_moderation_action(
            SocialModerationAction(
                moderator_user_id=moderator_user_id,
                target_type=SocialModerationTargetType.COMMENT.value,
                post_id=None,
                comment_id=row.id,
                action_type=SocialModerationActionType.UNHIDE.value,
                reason=payload.reason,
                metadata_json=None,
            )
        )

        self.repo.commit()
        self.repo.refresh(row)

        return SocialAdminCommentOut.model_validate(row)

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

        if row.author_user_id != moderator_user_id:
            self._notify_user(
                recipient_user_id=row.author_user_id,
                event_type=NotificationEventType.SOCIAL_POST_HIDDEN.value,
                title="پست شما مخفی شد",
                body=f"پست «{row.title}» توسط تیم مدیریت مخفی شد.",
                source_type="social_post",
                source_id=str(row.id),
                payload_json={
                    "post_id": row.id,
                    "moderator_user_id": moderator_user_id,
                    "reason": payload.reason,
                },
                action_url=f"/social/posts/{row.id}",
                priority="high",
            )

        self.repo.commit()
        self.repo.refresh(row)

        return self._social_post_out(row)

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

        return self._social_post_out(row)

    def _notify_user(
        self,
        *,
        recipient_user_id: int,
        event_type: str,
        title: str,
        body: str,
        source_type: str,
        source_id: str,
        payload_json: dict,
        action_url: str | None = None,
        priority: str = "normal",
    ) -> None:
        NotificationService(self.db).create_event_and_notify_many(
            event_type=event_type,
            recipient_user_ids=[recipient_user_id],
            title=title,
            body=body,
            actor_user_id=None,
            source_type=source_type,
            source_id=source_id,
            payload_json=payload_json,
            action_url=action_url,
            priority=priority,
            commit=False,
        )

    def _notify_social_admins(
        self,
        *,
        event_type: str,
        title: str,
        body: str,
        source_type: str,
        source_id: str,
        payload_json: dict,
        action_url: str | None = None,
        priority: str = "normal",
    ) -> None:
        recipient_ids = self.repo.list_social_admin_recipient_user_ids()

        if not recipient_ids:
            return

        NotificationService(self.db).create_event_and_notify_many(
            event_type=event_type,
            recipient_user_ids=recipient_ids,
            title=title,
            body=body,
            actor_user_id=None,
            source_type=source_type,
            source_id=source_id,
            payload_json=payload_json,
            action_url=action_url,
            priority=priority,
            commit=False,
        )

    def _validate_social_post_media(
        self,
        *,
        media_file_id: int | None,
        author_user_id: int,
    ) -> None:
        if media_file_id is None:
            return

        media = self.repo.get_media_file_by_id(media_file_id=media_file_id)

        if media is None:
            raise ValidationAuthError(
                message="Media file not found",
                details={"media_file_id": media_file_id},
            )

        if media.owner_user_id != author_user_id:
            raise ValidationAuthError(
                message="Media file not found",
                details={"media_file_id": media_file_id},
            )

        if media.purpose != MediaPurpose.SOCIAL_POST_IMAGE.value:
            raise ValidationAuthError(
                message="Invalid media purpose for social post",
                details={"media_file_id": media_file_id},
            )

        if media.visibility != MediaVisibility.PUBLIC.value:
            raise ValidationAuthError(
                message="Social post image must be public",
                details={"media_file_id": media_file_id},
            )

        if media.status != MediaStatus.ACTIVE.value:
            raise ValidationAuthError(
                message="Media file is not active",
                details={"media_file_id": media_file_id},
            )

    def _social_post_out(self, row: SocialPost) -> SocialPostOut:
        result = SocialPostOut.model_validate(row)

        if row.media_file_id is None:
            return result

        media = self.repo.get_media_file_by_id(media_file_id=row.media_file_id)

        if (
            media is None
            or media.purpose != MediaPurpose.SOCIAL_POST_IMAGE.value
            or media.visibility != MediaVisibility.PUBLIC.value
            or media.status != MediaStatus.ACTIVE.value
        ):
            return result

        result.media_public_url = self._media_public_url(file_key=media.file_key)
        return result

    def _social_post_detail_out(self, row: SocialPost) -> SocialPostDetailOut:
        post_out = self._social_post_out(row)
        expert_answers, _ = ExpertAnswerService(self.db).list_published_answers_for_post(
            post_id=row.id,
            page=1,
            page_size=20,
        )

        return SocialPostDetailOut(
            **post_out.model_dump(),
            expert_answers=expert_answers,
        )

    def _media_public_url(self, *, file_key: str | None) -> str | None:
        if not file_key:
            return None

        return f"/api/v1/media/public/{file_key}"

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

    def _validate_post_status(self, status: str) -> None:
        allowed = {item.value for item in SocialPostStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid social post status",
                details={"allowed": sorted(allowed)},
            )

    def _validate_comment_status(self, status: str) -> None:
        allowed = {item.value for item in SocialCommentStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid social comment status",
                details={"allowed": sorted(allowed)},
            )

    def _validate_reaction_type(self, reaction_type: str) -> None:
        allowed = {item.value for item in SocialReactionType}

        if reaction_type not in allowed:
            raise ValidationAuthError(
                message="Invalid social reaction type",
                details={"allowed": sorted(allowed)},
            )

    def _validate_report_reason(self, reason: str) -> None:
        allowed = {item.value for item in SocialReportReason}

        if reason not in allowed:
            raise ValidationAuthError(
                message="Invalid social report reason",
                details={"allowed": sorted(allowed)},
            )

    def _validate_report_status(self, status: str) -> None:
        allowed = {item.value for item in SocialReportStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid social report status",
                details={"allowed": sorted(allowed)},
            )

    def _validate_report_target_type(self, target_type: str) -> None:
        allowed = {item.value for item in SocialReportTargetType}

        if target_type not in allowed:
            raise ValidationAuthError(
                message="Invalid social report target type",
                details={"allowed": sorted(allowed)},
            )
