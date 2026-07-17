"""add checkout idempotency

Revision ID: b84d1c7e29f0
Revises: a7c9f2e14b30
Create Date: 2026-07-17
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "b84d1c7e29f0"
down_revision: str | Sequence[str] | None = "a7c9f2e14b30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "checkout_requests",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("cart_id", sa.BigInteger(), nullable=False),
        sa.Column("idempotency_key", sa.String(160), nullable=False),
        sa.Column("request_fingerprint", sa.String(64), nullable=False),
        sa.Column("order_ids", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cart_id"], ["carts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_checkout_requests_user_key"),
    )
    op.create_index("ix_checkout_requests_user_id", "checkout_requests", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_checkout_requests_user_id", table_name="checkout_requests")
    op.drop_table("checkout_requests")
