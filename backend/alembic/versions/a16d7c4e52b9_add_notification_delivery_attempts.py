"""add notification delivery attempts

Revision ID: a16d7c4e52b9
Revises: f84c2a1d9037
Create Date: 2026-07-18 10:30:00

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "a16d7c4e52b9"
down_revision: str | Sequence[str] | None = "f84c2a1d9037"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notification_delivery_attempts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("delivery_log_id", sa.BigInteger(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["delivery_log_id"],
            ["notification_delivery_logs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "delivery_log_id",
            "attempt_number",
            name="uq_notification_delivery_attempt_number",
        ),
    )
    op.create_index(
        op.f("ix_notification_delivery_attempts_delivery_log_id"),
        "notification_delivery_attempts",
        ["delivery_log_id"],
        unique=False,
    )
    op.create_index(
        "ix_notification_delivery_attempts_status_started",
        "notification_delivery_attempts",
        ["status", "started_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notification_delivery_attempts_status_started",
        table_name="notification_delivery_attempts",
    )
    op.drop_index(
        op.f("ix_notification_delivery_attempts_delivery_log_id"),
        table_name="notification_delivery_attempts",
    )
    op.drop_table("notification_delivery_attempts")
