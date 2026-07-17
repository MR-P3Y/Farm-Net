"""add notification devices

Revision ID: b27e8d5f64c1
Revises: a16d7c4e52b9
Create Date: 2026-07-18 12:00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "b27e8d5f64c1"
down_revision: str | Sequence[str] | None = "a16d7c4e52b9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notification_devices",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("token", sa.String(length=500), nullable=False),
        sa.Column("platform", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_notification_devices_user_active", "notification_devices", ["user_id", "is_active"], unique=False)
    op.create_index(op.f("ix_notification_devices_user_id"), "notification_devices", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notification_devices_user_id"), table_name="notification_devices")
    op.drop_index("ix_notification_devices_user_active", table_name="notification_devices")
    op.drop_table("notification_devices")
