"""add admin audit logs

Revision ID: c91e4a8d52b7
Revises: b84d1c7e29f0
Create Date: 2026-07-17
"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "c91e4a8d52b7"
down_revision: str | Sequence[str] | None = "b84d1c7e29f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("admin_user_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(80), nullable=False),
        sa.Column("target_id", sa.String(100), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("trace_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["admin_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("admin_user_id", "action", "target_type", "trace_id"):
        op.create_index(f"ix_admin_audit_logs_{column}", "admin_audit_logs", [column])


def downgrade() -> None:
    for column in ("trace_id", "target_type", "action", "admin_user_id"):
        op.drop_index(f"ix_admin_audit_logs_{column}", table_name="admin_audit_logs")
    op.drop_table("admin_audit_logs")
