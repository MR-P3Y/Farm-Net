"""harden notification delivery contracts

Revision ID: e72b9f4c31a6
Revises: c91e4a8d52b7
Create Date: 2026-07-17 18:05:00

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "e72b9f4c31a6"
down_revision: str | Sequence[str] | None = "c91e4a8d52b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM notifications
        WHERE id IN (
            SELECT id FROM (
                SELECT id, row_number() OVER (
                    PARTITION BY event_id, recipient_user_id, channel ORDER BY id
                ) AS duplicate_number
                FROM notifications WHERE event_id IS NOT NULL
            ) ranked_notifications
            WHERE duplicate_number > 1
        )
        """
    )
    op.create_unique_constraint(
        "uq_notifications_event_recipient_channel",
        "notifications",
        ["event_id", "recipient_user_id", "channel"],
    )

    op.add_column(
        "notification_delivery_logs",
        sa.Column(
            "attempt_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column(
        "notification_delivery_logs",
        sa.Column(
            "max_attempts",
            sa.Integer(),
            server_default=sa.text("5"),
            nullable=False,
        ),
    )
    op.add_column(
        "notification_delivery_logs",
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "notification_delivery_logs",
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "notification_delivery_logs",
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        DELETE FROM notification_delivery_logs
        WHERE id IN (
            SELECT id FROM (
                SELECT id, row_number() OVER (
                    PARTITION BY notification_id, channel ORDER BY id
                ) AS duplicate_number
                FROM notification_delivery_logs
            ) ranked_delivery_logs
            WHERE duplicate_number > 1
        )
        """
    )
    op.create_unique_constraint(
        "uq_notification_delivery_notification_channel",
        "notification_delivery_logs",
        ["notification_id", "channel"],
    )
    op.create_index(
        "ix_notification_delivery_logs_retry_ready",
        "notification_delivery_logs",
        ["status", "next_attempt_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notification_delivery_logs_retry_ready",
        table_name="notification_delivery_logs",
    )
    op.drop_constraint(
        "uq_notification_delivery_notification_channel",
        "notification_delivery_logs",
        type_="unique",
    )
    op.drop_column("notification_delivery_logs", "locked_at")
    op.drop_column("notification_delivery_logs", "last_attempt_at")
    op.drop_column("notification_delivery_logs", "next_attempt_at")
    op.drop_column("notification_delivery_logs", "max_attempts")
    op.drop_column("notification_delivery_logs", "attempt_count")
    op.drop_constraint(
        "uq_notifications_event_recipient_channel",
        "notifications",
        type_="unique",
    )
