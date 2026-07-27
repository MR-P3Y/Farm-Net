"""add Barzegar smart diary suggestions and farmer reports

Revision ID: k21g8e5c1029
Revises: j21f7d4b0918
Create Date: 2026-07-28 03:10:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "k21g8e5c1029"
down_revision: str | Sequence[str] | None = "j21f7d4b0918"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_diary_suggestions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("farm_id", sa.BigInteger(), nullable=False),
        sa.Column("plot_id", sa.BigInteger(), nullable=False),
        sa.Column("crop_cycle_id", sa.BigInteger(), nullable=False),
        sa.Column("proposed_operation", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("farm_operation_id", sa.BigInteger(), nullable=True),
        sa.Column("rejection_reason", sa.String(length=500), nullable=True),
        sa.Column("decided_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending','accepted','rejected')",
            name="ck_ai_diary_suggestions_status",
        ),
        sa.CheckConstraint(
            "(status = 'pending' AND decided_at IS NULL AND farm_operation_id IS NULL) OR "
            "(status = 'accepted' AND decided_at IS NOT NULL AND farm_operation_id IS NOT NULL) OR "
            "(status = 'rejected' AND decided_at IS NOT NULL AND farm_operation_id IS NULL)",
            name="ck_ai_diary_suggestions_decision",
        ),
        sa.ForeignKeyConstraint(["crop_cycle_id"], ["farm_crop_cycles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["farm_operation_id"], ["farm_operations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["plot_id"], ["farm_plots.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["request_id"], ["ai_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("farm_operation_id"),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index(
        "ix_ai_diary_suggestions_owner_status",
        "ai_diary_suggestions",
        ["user_id", "status", "created_at"],
    )
    op.create_table(
        "ai_farmer_reports",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("farm_id", sa.BigInteger(), nullable=False),
        sa.Column("plot_id", sa.BigInteger(), nullable=True),
        sa.Column("crop_cycle_id", sa.BigInteger(), nullable=True),
        sa.Column("source_snapshot", sa.JSON(), nullable=False),
        sa.Column("narrative", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("CHAR_LENGTH(narrative) > 0", name="ck_ai_farmer_reports_narrative"),
        sa.ForeignKeyConstraint(["crop_cycle_id"], ["farm_crop_cycles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["plot_id"], ["farm_plots.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["request_id"], ["ai_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index(
        "ix_ai_farmer_reports_owner_generated",
        "ai_farmer_reports",
        ["user_id", "generated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_ai_farmer_reports_owner_generated", table_name="ai_farmer_reports")
    op.drop_table("ai_farmer_reports")
    op.drop_index("ix_ai_diary_suggestions_owner_status", table_name="ai_diary_suggestions")
    op.drop_table("ai_diary_suggestions")
