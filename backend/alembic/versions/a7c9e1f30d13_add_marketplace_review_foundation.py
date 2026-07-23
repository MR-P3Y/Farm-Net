"""add marketplace review foundation

Revision ID: a7c9e1f30d13
Revises: fdcb2ab80c12
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "a7c9e1f30d13"
down_revision: str | None = "fdcb2ab80c12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


SUBJECT_TYPE_CHECK = (
    "subject_type IN "
    "('product', 'store', 'service_offer', 'service_provider', "
    "'rental_equipment', 'rental_lessor', 'consultant')"
)


def upgrade() -> None:
    op.create_table(
        "marketplace_reviews",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("reviewer_user_id", sa.BigInteger(), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("subject_type", sa.String(length=40), nullable=False),
        sa.Column("subject_id", sa.BigInteger(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "(status = 'deleted' AND deleted_at IS NOT NULL) OR "
            "(status <> 'deleted' AND deleted_at IS NULL)",
            name="ck_marketplace_review_deleted_state",
        ),
        sa.CheckConstraint(
            "score BETWEEN 1 AND 5",
            name="ck_marketplace_review_score",
        ),
        sa.CheckConstraint(
            "source_id > 0",
            name="ck_marketplace_review_source_id_positive",
        ),
        sa.CheckConstraint(
            "source_type IN "
            "('order', 'service_request', 'rental_request', 'consult_request')",
            name="ck_marketplace_review_source_type",
        ),
        sa.CheckConstraint(
            "(source_type = 'order' AND subject_type IN ('product', 'store')) OR "
            "(source_type = 'service_request' AND "
            "subject_type IN ('service_offer', 'service_provider')) OR "
            "(source_type = 'rental_request' AND "
            "subject_type IN ('rental_equipment', 'rental_lessor')) OR "
            "(source_type = 'consult_request' AND subject_type = 'consultant')",
            name="ck_marketplace_review_source_subject",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'hidden', 'deleted')",
            name="ck_marketplace_review_status",
        ),
        sa.CheckConstraint(
            "subject_id > 0",
            name="ck_marketplace_review_subject_id_positive",
        ),
        sa.CheckConstraint(
            SUBJECT_TYPE_CHECK,
            name="ck_marketplace_review_subject_type",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_user_id"],
            ["auth_users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "reviewer_user_id",
            "source_type",
            "source_id",
            "subject_type",
            "subject_id",
            name="uq_marketplace_review_eligibility",
        ),
    )
    op.create_index(
        op.f("ix_marketplace_reviews_reviewer_user_id"),
        "marketplace_reviews",
        ["reviewer_user_id"],
    )
    op.create_index(
        op.f("ix_marketplace_reviews_source_type"),
        "marketplace_reviews",
        ["source_type"],
    )
    op.create_index(
        op.f("ix_marketplace_reviews_subject_type"),
        "marketplace_reviews",
        ["subject_type"],
    )
    op.create_index(
        op.f("ix_marketplace_reviews_status"),
        "marketplace_reviews",
        ["status"],
    )
    op.create_index(
        "ix_marketplace_reviews_subject_public",
        "marketplace_reviews",
        ["subject_type", "subject_id", "status", "created_at"],
    )
    op.create_index(
        "ix_marketplace_reviews_reviewer_created",
        "marketplace_reviews",
        ["reviewer_user_id", "created_at"],
    )
    op.create_index(
        "ix_marketplace_reviews_source",
        "marketplace_reviews",
        ["source_type", "source_id"],
    )

    op.create_table(
        "marketplace_rating_aggregates",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("subject_type", sa.String(length=40), nullable=False),
        sa.Column("subject_id", sa.BigInteger(), nullable=False),
        sa.Column("rating_sum", sa.BigInteger(), nullable=False),
        sa.Column("reviews_count", sa.BigInteger(), nullable=False),
        sa.Column("rating_average", sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "rating_average >= 0 AND rating_average <= 5",
            name="ck_marketplace_rating_average_range",
        ),
        sa.CheckConstraint(
            "reviews_count >= 0",
            name="ck_marketplace_rating_count_nonnegative",
        ),
        sa.CheckConstraint(
            "subject_id > 0",
            name="ck_marketplace_rating_subject_id_positive",
        ),
        sa.CheckConstraint(
            "(reviews_count = 0 AND rating_sum = 0 AND rating_average = 0) OR "
            "(reviews_count > 0 AND rating_sum >= reviews_count)",
            name="ck_marketplace_rating_empty_or_scored",
        ),
        sa.CheckConstraint(
            "rating_sum >= 0 AND rating_sum <= reviews_count * 5",
            name="ck_marketplace_rating_sum_range",
        ),
        sa.CheckConstraint(
            SUBJECT_TYPE_CHECK,
            name="ck_marketplace_rating_subject_type",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "subject_type",
            "subject_id",
            name="uq_marketplace_rating_subject",
        ),
    )
    op.create_index(
        "ix_marketplace_rating_rank",
        "marketplace_rating_aggregates",
        ["subject_type", "rating_average", "reviews_count"],
    )

    op.create_table(
        "marketplace_review_reports",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("review_id", sa.BigInteger(), nullable=False),
        sa.Column("reporter_user_id", sa.BigInteger(), nullable=False),
        sa.Column("reason", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("reviewed_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("resolution_note", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "reason IN ('spam', 'abuse', 'harassment', 'privacy', 'fraud', 'other')",
            name="ck_marketplace_review_report_reason",
        ),
        sa.CheckConstraint(
            "(status = 'open' AND reviewed_at IS NULL) OR "
            "(status <> 'open' AND reviewed_at IS NOT NULL)",
            name="ck_marketplace_review_report_review_state",
        ),
        sa.CheckConstraint(
            "status IN ('open', 'reviewed', 'resolved', 'dismissed')",
            name="ck_marketplace_review_report_status",
        ),
        sa.ForeignKeyConstraint(
            ["reporter_user_id"],
            ["auth_users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["review_id"],
            ["marketplace_reviews.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by_user_id"],
            ["auth_users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "review_id",
            "reporter_user_id",
            name="uq_marketplace_review_reporter",
        ),
    )
    for column in (
        "review_id",
        "reporter_user_id",
        "status",
        "reviewed_by_user_id",
    ):
        op.create_index(
            op.f(f"ix_marketplace_review_reports_{column}"),
            "marketplace_review_reports",
            [column],
        )
    op.create_index(
        "ix_marketplace_review_reports_status_created",
        "marketplace_review_reports",
        ["status", "created_at"],
    )

    op.create_table(
        "marketplace_review_moderation_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("review_id", sa.BigInteger(), nullable=False),
        sa.Column("actor_user_id", sa.BigInteger(), nullable=True),
        sa.Column("report_id", sa.BigInteger(), nullable=True),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("from_status", sa.String(length=30), nullable=True),
        sa.Column("to_status", sa.String(length=30), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("event_key", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "action IN "
            "('hidden', 'restored', 'deleted', 'report_reviewed', "
            "'report_resolved', 'report_dismissed')",
            name="ck_marketplace_review_moderation_action",
        ),
        sa.CheckConstraint(
            "from_status IS NULL OR from_status IN ('active', 'hidden', 'deleted')",
            name="ck_marketplace_review_moderation_from_status",
        ),
        sa.CheckConstraint(
            "to_status IS NULL OR to_status IN ('active', 'hidden', 'deleted')",
            name="ck_marketplace_review_moderation_to_status",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["auth_users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["marketplace_review_reports.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["review_id"],
            ["marketplace_reviews.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_key"),
    )
    for column in ("review_id", "actor_user_id", "report_id", "action"):
        op.create_index(
            op.f(f"ix_marketplace_review_moderation_logs_{column}"),
            "marketplace_review_moderation_logs",
            [column],
        )
    op.create_index(
        "ix_marketplace_review_moderation_review_created",
        "marketplace_review_moderation_logs",
        ["review_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_table("marketplace_review_moderation_logs")
    op.drop_table("marketplace_review_reports")
    op.drop_table("marketplace_rating_aggregates")
    op.drop_table("marketplace_reviews")
