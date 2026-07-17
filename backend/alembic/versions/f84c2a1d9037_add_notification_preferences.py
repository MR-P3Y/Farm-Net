"""add notification preferences

Revision ID: f84c2a1d9037
Revises: e72b9f4c31a6
Create Date: 2026-07-18 09:00:00

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "f84c2a1d9037"
down_revision: str | Sequence[str] | None = "e72b9f4c31a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "event_type", sa.String(length=80), server_default="*", nullable=False
        ),
        sa.Column("channel", sa.String(length=30), nullable=False),
        sa.Column(
            "is_enabled",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "event_type",
            "channel",
            name="uq_notification_preferences_user_event_channel",
        ),
    )
    op.create_index(
        "ix_notification_preferences_user_event",
        "notification_preferences",
        ["user_id", "event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_preferences_user_id"),
        "notification_preferences",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_notification_preferences_user_id"),
        table_name="notification_preferences",
    )
    op.drop_index(
        "ix_notification_preferences_user_event",
        table_name="notification_preferences",
    )
    op.drop_table("notification_preferences")
