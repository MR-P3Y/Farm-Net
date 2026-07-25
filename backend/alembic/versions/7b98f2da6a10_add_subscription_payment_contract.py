"""add subscription payment contract

Revision ID: 7b98f2da6a10
Revises: 96f4165b43fe
Create Date: 2026-07-26 01:40:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "7b98f2da6a10"
down_revision: str | Sequence[str] | None = "96f4165b43fe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "finance_billing_invoices",
        "provider_user_id",
        existing_type=sa.BigInteger(),
        nullable=True,
    )
    op.create_check_constraint(
        "ck_billing_invoice_platform_owner",
        "finance_billing_invoices",
        "(source_type = 'platform_subscription' AND provider_user_id IS NULL "
        "AND provider_amount = 0 AND platform_amount = total_amount) OR "
        "(source_type <> 'platform_subscription' AND provider_user_id IS NOT NULL)",
    )
    op.create_table(
        "billing_subscription_payment_attempts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("subscription_id", sa.BigInteger(), nullable=False),
        sa.Column("invoice_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("amount_toman", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("idempotency_key", sa.String(length=180), nullable=False),
        sa.Column("provider_authority", sa.String(length=255), nullable=True),
        sa.Column("provider_reference", sa.String(length=255), nullable=True),
        sa.Column("redirect_url", sa.Text(), nullable=True),
        sa.Column("failure_code", sa.String(length=100), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("verified_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("amount_toman > 0", name="ck_subscription_payment_amount"),
        sa.CheckConstraint("currency = 'TOMAN'", name="ck_subscription_payment_currency"),
        sa.CheckConstraint(
            "provider IN ('mock', 'zarinpal')", name="ck_subscription_payment_provider"
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'redirected', 'verifying', 'succeeded', 'failed', 'cancelled')",
            name="ck_subscription_payment_status",
        ),
        sa.ForeignKeyConstraint(
            ["invoice_id"], ["finance_billing_invoices.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id"], ["billing_subscriptions.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
        sa.UniqueConstraint("provider_authority"),
        sa.UniqueConstraint("provider_reference"),
    )
    op.create_index(
        op.f("ix_billing_subscription_payment_attempts_invoice_id"),
        "billing_subscription_payment_attempts",
        ["invoice_id"],
    )
    op.create_index(
        op.f("ix_billing_subscription_payment_attempts_status"),
        "billing_subscription_payment_attempts",
        ["status"],
    )
    op.create_index(
        op.f("ix_billing_subscription_payment_attempts_subscription_id"),
        "billing_subscription_payment_attempts",
        ["subscription_id"],
    )
    op.create_index(
        op.f("ix_billing_subscription_payment_attempts_user_id"),
        "billing_subscription_payment_attempts",
        ["user_id"],
    )
    op.create_index(
        "ix_subscription_payment_user_status",
        "billing_subscription_payment_attempts",
        ["user_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_subscription_payment_user_status",
        table_name="billing_subscription_payment_attempts",
    )
    op.drop_index(
        op.f("ix_billing_subscription_payment_attempts_user_id"),
        table_name="billing_subscription_payment_attempts",
    )
    op.drop_index(
        op.f("ix_billing_subscription_payment_attempts_subscription_id"),
        table_name="billing_subscription_payment_attempts",
    )
    op.drop_index(
        op.f("ix_billing_subscription_payment_attempts_status"),
        table_name="billing_subscription_payment_attempts",
    )
    op.drop_index(
        op.f("ix_billing_subscription_payment_attempts_invoice_id"),
        table_name="billing_subscription_payment_attempts",
    )
    op.drop_table("billing_subscription_payment_attempts")
    op.drop_constraint(
        "ck_billing_invoice_platform_owner",
        "finance_billing_invoices",
        type_="check",
    )
    op.alter_column(
        "finance_billing_invoices",
        "provider_user_id",
        existing_type=sa.BigInteger(),
        nullable=False,
    )
