"""add password reset challenges

Revision ID: s26g7h8i9j0k
Revises: r26f6a7b8c9d
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "s26g7h8i9j0k"
down_revision: str | None = "r26f6a7b8c9d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "auth_password_reset_challenges",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("identifier_hash", sa.String(length=64), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth_users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_auth_password_reset_challenges_identifier_status_created",
        "auth_password_reset_challenges",
        ["identifier_hash", "status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_auth_password_reset_challenges_status",
        "auth_password_reset_challenges",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_auth_password_reset_challenges_user_status",
        "auth_password_reset_challenges",
        ["user_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_auth_password_reset_challenges_user_status",
        table_name="auth_password_reset_challenges",
    )
    op.drop_index(
        "ix_auth_password_reset_challenges_status",
        table_name="auth_password_reset_challenges",
    )
    op.drop_index(
        "ix_auth_password_reset_challenges_identifier_status_created",
        table_name="auth_password_reset_challenges",
    )
    op.drop_table("auth_password_reset_challenges")
