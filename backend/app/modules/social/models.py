from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.media import models as media_models  # noqa: F401


class SocialCategory(Base):
    __tablename__ = "social_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    sort_order: Mapped[int] = mapped_column(BigInteger, nullable=False, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_social_categories_active_sort", "is_active", "sort_order"),
    )


class SocialPost(Base):
    __tablename__ = "social_posts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    author_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("social_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    post_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="published")
    visibility: Mapped[str] = mapped_column(String(40), nullable=False, default="public")

    media_file_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("media_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    country_code: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
        index=True,
    )
    province_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    city_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    village_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)

    province_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    village_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    latitude: Mapped[str | None] = mapped_column(String(40), nullable=True)
    longitude: Mapped[str | None] = mapped_column(String(40), nullable=True)

    views_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    comments_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    reactions_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    reports_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    published_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    deleted_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_social_posts_status_created", "status", "created_at"),
        Index("ix_social_posts_type_status_created", "post_type", "status", "created_at"),
        Index(
            "ix_social_posts_category_status_created",
            "category_id",
            "status",
            "created_at",
        ),
        Index("ix_social_posts_geo", "province_id", "city_id", "village_id"),
    )


class SocialComment(Base):
    __tablename__ = "social_comments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("social_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    author_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_comment_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("social_comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="published")

    reactions_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    reports_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    deleted_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_social_comments_post_status_created", "post_id", "status", "created_at"),
        Index("ix_social_comments_parent_created", "parent_comment_id", "created_at"),
    )


class SocialReaction(Base):
    __tablename__ = "social_reactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    post_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("social_posts.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    comment_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("social_comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reaction_type: Mapped[str] = mapped_column(String(40), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "post_id",
            "comment_id",
            "user_id",
            "reaction_type",
            name="uq_social_reactions_target_user_type",
        ),
        Index("ix_social_reactions_user_created", "user_id", "created_at"),
    )


class SocialBookmark(Base):
    __tablename__ = "social_bookmarks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("social_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_social_bookmarks_post_user"),
        Index("ix_social_bookmarks_user_created", "user_id", "created_at"),
    )


class SocialReport(Base):
    __tablename__ = "social_reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    reporter_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_type: Mapped[str] = mapped_column(String(40), nullable=False)

    post_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("social_posts.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    comment_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("social_comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    reason: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(40), nullable=False, default="open")

    reviewed_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reviewed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_social_reports_target_status", "target_type", "status"),
        Index("ix_social_reports_status_created", "status", "created_at"),
    )


class SocialModerationAction(Base):
    __tablename__ = "social_moderation_actions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    moderator_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_type: Mapped[str] = mapped_column(String(40), nullable=False)

    post_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("social_posts.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    comment_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("social_comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    action_type: Mapped[str] = mapped_column(String(40), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_social_moderation_target_created", "target_type", "created_at"),
        Index(
            "ix_social_moderation_moderator_created",
            "moderator_user_id",
            "created_at",
        ),
    )
