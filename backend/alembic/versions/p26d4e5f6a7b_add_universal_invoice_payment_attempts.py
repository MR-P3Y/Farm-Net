"""add universal invoice payment attempts

Revision ID: p26d4e5f6a7b
Revises: o26c3d4e5f6a
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "p26d4e5f6a7b"
down_revision: str | None = "o26c3d4e5f6a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "finance_billing_payment_attempts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
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
        sa.CheckConstraint(
            "provider IN ('mock', 'zarinpal')",
            name="ck_billing_payment_attempt_provider",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'redirected', 'verifying', 'succeeded', 'failed', 'cancelled')",
            name="ck_billing_payment_attempt_status",
        ),
        sa.CheckConstraint("amount_toman > 0", name="ck_billing_payment_attempt_amount"),
        sa.CheckConstraint("currency = 'TOMAN'", name="ck_billing_payment_attempt_currency"),
        sa.ForeignKeyConstraint(
            ["invoice_id"], ["finance_billing_invoices.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
        sa.UniqueConstraint("provider_authority"),
        sa.UniqueConstraint("provider_reference"),
    )
    op.create_index(
        "ix_finance_billing_payment_attempts_invoice_id",
        "finance_billing_payment_attempts",
        ["invoice_id"],
    )
    op.create_index(
        "ix_finance_billing_payment_attempts_user_id",
        "finance_billing_payment_attempts",
        ["user_id"],
    )
    op.create_index(
        "ix_finance_billing_payment_attempts_status",
        "finance_billing_payment_attempts",
        ["status"],
    )
    op.create_index(
        "ix_billing_payment_attempt_user_status",
        "finance_billing_payment_attempts",
        ["user_id", "status"],
    )
    op.create_index(
        "ix_billing_payment_attempt_invoice_status",
        "finance_billing_payment_attempts",
        ["invoice_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_billing_payment_attempt_invoice_status",
        table_name="finance_billing_payment_attempts",
    )
    op.drop_index(
        "ix_billing_payment_attempt_user_status",
        table_name="finance_billing_payment_attempts",
    )
    op.drop_index(
        "ix_finance_billing_payment_attempts_status",
        table_name="finance_billing_payment_attempts",
    )
    op.drop_index(
        "ix_finance_billing_payment_attempts_user_id",
        table_name="finance_billing_payment_attempts",
    )
    op.drop_index(
        "ix_finance_billing_payment_attempts_invoice_id",
        table_name="finance_billing_payment_attempts",
    )
    op.drop_table("finance_billing_payment_attempts")
