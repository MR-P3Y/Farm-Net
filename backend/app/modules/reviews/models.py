from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.reviews.enums import (
    ReviewReportStatus,
    ReviewStatus,
)


class MarketplaceReview(Base):
    __tablename__ = "marketplace_reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reviewer_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    source_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    subject_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=ReviewStatus.ACTIVE.value,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    reports: Mapped[list["MarketplaceReviewReport"]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
    )
    moderation_logs: Mapped[list["MarketplaceReviewModerationLog"]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "reviewer_user_id",
            "source_type",
            "source_id",
            "subject_type",
            "subject_id",
            name="uq_marketplace_review_eligibility",
        ),
        CheckConstraint("score BETWEEN 1 AND 5", name="ck_marketplace_review_score"),
        CheckConstraint(
            "source_id > 0",
            name="ck_marketplace_review_source_id_positive",
        ),
        CheckConstraint(
            "subject_id > 0",
            name="ck_marketplace_review_subject_id_positive",
        ),
        CheckConstraint(
            "source_type IN "
            "('order', 'service_request', 'rental_request', 'consult_request')",
            name="ck_marketplace_review_source_type",
        ),
        CheckConstraint(
            "subject_type IN "
            "('product', 'store', 'service_offer', 'service_provider', "
            "'rental_equipment', 'rental_lessor', 'consultant')",
            name="ck_marketplace_review_subject_type",
        ),
        CheckConstraint(
            "(source_type = 'order' AND subject_type IN ('product', 'store')) OR "
            "(source_type = 'service_request' AND "
            "subject_type IN ('service_offer', 'service_provider')) OR "
            "(source_type = 'rental_request' AND "
            "subject_type IN ('rental_equipment', 'rental_lessor')) OR "
            "(source_type = 'consult_request' AND subject_type = 'consultant')",
            name="ck_marketplace_review_source_subject",
        ),
        CheckConstraint(
            "status IN ('active', 'hidden', 'deleted')",
            name="ck_marketplace_review_status",
        ),
        CheckConstraint(
            "(status = 'deleted' AND deleted_at IS NOT NULL) OR "
            "(status <> 'deleted' AND deleted_at IS NULL)",
            name="ck_marketplace_review_deleted_state",
        ),
        Index(
            "ix_marketplace_reviews_subject_public",
            "subject_type",
            "subject_id",
            "status",
            "created_at",
        ),
        Index(
            "ix_marketplace_reviews_reviewer_created",
            "reviewer_user_id",
            "created_at",
        ),
        Index(
            "ix_marketplace_reviews_source",
            "source_type",
            "source_id",
        ),
    )


class MarketplaceRatingAggregate(Base):
    __tablename__ = "marketplace_rating_aggregates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    subject_type: Mapped[str] = mapped_column(String(40), nullable=False)
    subject_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rating_sum: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    reviews_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    rating_average: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "subject_type",
            "subject_id",
            name="uq_marketplace_rating_subject",
        ),
        CheckConstraint(
            "subject_type IN "
            "('product', 'store', 'service_offer', 'service_provider', "
            "'rental_equipment', 'rental_lessor', 'consultant')",
            name="ck_marketplace_rating_subject_type",
        ),
        CheckConstraint(
            "reviews_count >= 0",
            name="ck_marketplace_rating_count_nonnegative",
        ),
        CheckConstraint(
            "subject_id > 0",
            name="ck_marketplace_rating_subject_id_positive",
        ),
        CheckConstraint(
            "rating_sum >= 0 AND rating_sum <= reviews_count * 5",
            name="ck_marketplace_rating_sum_range",
        ),
        CheckConstraint(
            "rating_average >= 0 AND rating_average <= 5",
            name="ck_marketplace_rating_average_range",
        ),
        CheckConstraint(
            "(reviews_count = 0 AND rating_sum = 0 AND rating_average = 0) OR "
            "(reviews_count > 0 AND rating_sum >= reviews_count)",
            name="ck_marketplace_rating_empty_or_scored",
        ),
        Index(
            "ix_marketplace_rating_rank",
            "subject_type",
            "rating_average",
            "reviews_count",
        ),
    )


class MarketplaceReviewReport(Base):
    __tablename__ = "marketplace_review_reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("marketplace_reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reporter_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reason: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=ReviewReportStatus.OPEN.value,
        index=True,
    )
    reviewed_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    review: Mapped["MarketplaceReview"] = relationship(back_populates="reports")

    __table_args__ = (
        UniqueConstraint(
            "review_id",
            "reporter_user_id",
            name="uq_marketplace_review_reporter",
        ),
        CheckConstraint(
            "reason IN ('spam', 'abuse', 'harassment', 'privacy', 'fraud', 'other')",
            name="ck_marketplace_review_report_reason",
        ),
        CheckConstraint(
            "status IN ('open', 'reviewed', 'resolved', 'dismissed')",
            name="ck_marketplace_review_report_status",
        ),
        CheckConstraint(
            "(status = 'open' AND reviewed_at IS NULL) OR "
            "(status <> 'open' AND reviewed_at IS NOT NULL)",
            name="ck_marketplace_review_report_review_state",
        ),
        Index(
            "ix_marketplace_review_reports_status_created",
            "status",
            "created_at",
        ),
    )


class MarketplaceReviewModerationLog(Base):
    __tablename__ = "marketplace_review_moderation_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("marketplace_reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    report_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("marketplace_review_reports.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    from_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_key: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    review: Mapped["MarketplaceReview"] = relationship(
        back_populates="moderation_logs"
    )

    __table_args__ = (
        CheckConstraint(
            "action IN "
            "('hidden', 'restored', 'deleted', 'report_reviewed', "
            "'report_resolved', 'report_dismissed')",
            name="ck_marketplace_review_moderation_action",
        ),
        CheckConstraint(
            "from_status IS NULL OR from_status IN ('active', 'hidden', 'deleted')",
            name="ck_marketplace_review_moderation_from_status",
        ),
        CheckConstraint(
            "to_status IS NULL OR to_status IN ('active', 'hidden', 'deleted')",
            name="ck_marketplace_review_moderation_to_status",
        ),
        Index(
            "ix_marketplace_review_moderation_review_created",
            "review_id",
            "created_at",
        ),
    )
