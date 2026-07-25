"""add subscription admin activation provenance

Revision ID: d8f3a9c21b74
Revises: bc620ec4f128
Create Date: 2026-07-26 12:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "d8f3a9c21b74"
down_revision: str | Sequence[str] | None = "bc620ec4f128"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "billing_subscriptions",
        sa.Column(
            "activation_source",
            sa.String(length=20),
            nullable=False,
            server_default="self",
        ),
    )
    op.add_column(
        "billing_subscriptions",
        sa.Column("activated_by_user_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "billing_subscriptions",
        sa.Column("activation_reason", sa.String(length=500), nullable=True),
    )
    op.create_foreign_key(
        "fk_billing_subscriptions_activated_by_user",
        "billing_subscriptions",
        "auth_users",
        ["activated_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_check_constraint(
        "ck_billing_subscriptions_activation_source",
        "billing_subscriptions",
        "activation_source IN ('self', 'checkout', 'admin')",
    )
    op.alter_column("billing_subscriptions", "activation_source", server_default=None)


def downgrade() -> None:
    op.drop_constraint(
        "ck_billing_subscriptions_activation_source",
        "billing_subscriptions",
        type_="check",
    )
    op.drop_constraint(
        "fk_billing_subscriptions_activated_by_user",
        "billing_subscriptions",
        type_="foreignkey",
    )
    op.drop_column("billing_subscriptions", "activation_reason")
    op.drop_column("billing_subscriptions", "activated_by_user_id")
    op.drop_column("billing_subscriptions", "activation_source")
