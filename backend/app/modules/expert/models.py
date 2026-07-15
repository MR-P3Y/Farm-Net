from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.social import models as social_models  # noqa: F401


class ExpertAnswer(Base):
    __tablename__ = "expert_answers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("social_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expert_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="published",
        server_default="published",
        index=True,
    )

    is_accepted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        index=True,
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    accepted_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    helpful_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        server_default="0",
    )
    reports_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        server_default="0",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    post = relationship("SocialPost")
    expert_user = relationship("AuthUser", foreign_keys=[expert_user_id])
    accepted_by_user = relationship("AuthUser", foreign_keys=[accepted_by_user_id])

    __table_args__ = (
        Index(
            "ix_expert_answers_post_status_created",
            "post_id",
            "status",
            "created_at",
        ),
        Index(
            "ix_expert_answers_expert_status_created",
            "expert_user_id",
            "status",
            "created_at",
        ),
    )
