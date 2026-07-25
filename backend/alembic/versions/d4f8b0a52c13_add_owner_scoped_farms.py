"""add owner scoped farms

Revision ID: d4f8b0a52c13
Revises: c3e7a9f41b02
Create Date: 2026-07-25 22:30:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "d4f8b0a52c13"
down_revision: str | Sequence[str] | None = "c3e7a9f41b02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "farms",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("archive_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "(status = 'active' AND archived_at IS NULL AND archive_reason IS NULL) "
            "OR (status = 'archived' AND archived_at IS NOT NULL)",
            name="ck_farms_archive_state",
        ),
        sa.CheckConstraint(
            "status in ('active', 'archived')",
            name="ck_farms_status",
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["auth_users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farms_owner_user_id"), "farms", ["owner_user_id"])
    op.create_index(op.f("ix_farms_status"), "farms", ["status"])
    op.create_index(
        "ix_farms_owner_status_updated",
        "farms",
        ["owner_user_id", "status", "updated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_farms_owner_status_updated", table_name="farms")
    op.drop_index(op.f("ix_farms_status"), table_name="farms")
    op.drop_index(op.f("ix_farms_owner_user_id"), table_name="farms")
    op.drop_table("farms")
