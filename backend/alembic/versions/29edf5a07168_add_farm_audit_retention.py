"""add farm audit retention

Revision ID: 29edf5a07168
Revises: 18dcf4e96057
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "29edf5a07168"
down_revision: str | Sequence[str] | None = "18dcf4e96057"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "farm_audit_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("farm_id", sa.BigInteger(), nullable=False),
        sa.Column("actor_user_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(80), nullable=False),
        sa.Column("target_id", sa.BigInteger(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farm_audit_logs_farm_id"), "farm_audit_logs", ["farm_id"])
    op.create_index(op.f("ix_farm_audit_logs_actor_user_id"), "farm_audit_logs", ["actor_user_id"])
    op.create_index(op.f("ix_farm_audit_logs_action"), "farm_audit_logs", ["action"])
    op.create_index(op.f("ix_farm_audit_logs_target_type"), "farm_audit_logs", ["target_type"])
    op.create_index("ix_farm_audit_logs_farm_created", "farm_audit_logs", ["farm_id", "created_at"])
    op.create_index("ix_farm_audit_logs_target", "farm_audit_logs", ["target_type", "target_id"])


def downgrade() -> None:
    op.drop_table("farm_audit_logs")
