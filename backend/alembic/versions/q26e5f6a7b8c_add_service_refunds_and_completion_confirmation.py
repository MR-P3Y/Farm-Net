"""add service refunds and completion confirmation

Revision ID: q26e5f6a7b8c
Revises: p26d4e5f6a7b
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "q26e5f6a7b8c"
down_revision: str | None = "p26d4e5f6a7b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "service_requests",
        sa.Column("completion_confirmed_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "service_requests",
        sa.Column("completion_confirmed_by_user_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_service_requests_completion_confirmed_by_user_id",
        "service_requests",
        "auth_users",
        ["completion_confirmed_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_service_requests_completion_confirmed_by_user_id",
        "service_requests",
        ["completion_confirmed_by_user_id"],
    )

    op.create_table(
        "finance_billing_refunds",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.BigInteger(), nullable=False),
        sa.Column("payment_attempt_id", sa.BigInteger(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("payer_user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider_user_id", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("amount_toman", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("idempotency_key", sa.String(length=180), nullable=False),
        sa.Column("reason", sa.String(length=1000), nullable=False),
        sa.Column("review_required", sa.Boolean(), nullable=False),
        sa.Column("provider_reference", sa.String(length=255), nullable=True),
        sa.Column("requested_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("decided_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("admin_note", sa.String(length=1000), nullable=True),
        sa.Column("requested_at", sa.DateTime(), nullable=False),
        sa.Column("decided_at", sa.DateTime(), nullable=True),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "source_type IN ('service_request', 'consultation_request')",
            name="ck_billing_refund_source_type",
        ),
        sa.CheckConstraint(
            "status IN ('requested', 'approved', 'succeeded', 'rejected')",
            name="ck_billing_refund_status",
        ),
        sa.CheckConstraint("amount_toman > 0", name="ck_billing_refund_amount"),
        sa.CheckConstraint("currency = 'TOMAN'", name="ck_billing_refund_currency"),
        sa.ForeignKeyConstraint(
            ["invoice_id"], ["finance_billing_invoices.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["payment_attempt_id"],
            ["finance_billing_payment_attempts.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payer_user_id"], ["auth_users.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["provider_user_id"], ["auth_users.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"], ["auth_users.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["decided_by_user_id"], ["auth_users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
        sa.UniqueConstraint("invoice_id"),
        sa.UniqueConstraint("provider_reference"),
    )
    op.create_index(
        "ix_finance_billing_refunds_invoice_id",
        "finance_billing_refunds",
        ["invoice_id"],
    )
    op.create_index(
        "ix_finance_billing_refunds_payment_attempt_id",
        "finance_billing_refunds",
        ["payment_attempt_id"],
    )
    op.create_index(
        "ix_finance_billing_refunds_source_type",
        "finance_billing_refunds",
        ["source_type"],
    )
    op.create_index(
        "ix_finance_billing_refunds_source_id",
        "finance_billing_refunds",
        ["source_id"],
    )
    op.create_index(
        "ix_finance_billing_refunds_payer_user_id",
        "finance_billing_refunds",
        ["payer_user_id"],
    )
    op.create_index(
        "ix_finance_billing_refunds_provider_user_id",
        "finance_billing_refunds",
        ["provider_user_id"],
    )
    op.create_index(
        "ix_finance_billing_refunds_status",
        "finance_billing_refunds",
        ["status"],
    )
    op.create_index(
        "ix_finance_billing_refunds_requested_by_user_id",
        "finance_billing_refunds",
        ["requested_by_user_id"],
    )
    op.create_index(
        "ix_finance_billing_refunds_decided_by_user_id",
        "finance_billing_refunds",
        ["decided_by_user_id"],
    )
    op.create_index(
        "ix_billing_refund_source",
        "finance_billing_refunds",
        ["source_type", "source_id"],
    )
    op.create_index(
        "ix_billing_refund_status_requested",
        "finance_billing_refunds",
        ["status", "requested_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_billing_refund_status_requested", table_name="finance_billing_refunds"
    )
    op.drop_index("ix_billing_refund_source", table_name="finance_billing_refunds")
    op.drop_index(
        "ix_finance_billing_refunds_decided_by_user_id",
        table_name="finance_billing_refunds",
    )
    op.drop_index(
        "ix_finance_billing_refunds_requested_by_user_id",
        table_name="finance_billing_refunds",
    )
    op.drop_index("ix_finance_billing_refunds_status", table_name="finance_billing_refunds")
    op.drop_index(
        "ix_finance_billing_refunds_provider_user_id",
        table_name="finance_billing_refunds",
    )
    op.drop_index(
        "ix_finance_billing_refunds_payer_user_id",
        table_name="finance_billing_refunds",
    )
    op.drop_index(
        "ix_finance_billing_refunds_source_id", table_name="finance_billing_refunds"
    )
    op.drop_index(
        "ix_finance_billing_refunds_source_type", table_name="finance_billing_refunds"
    )
    op.drop_index(
        "ix_finance_billing_refunds_payment_attempt_id",
        table_name="finance_billing_refunds",
    )
    op.drop_index(
        "ix_finance_billing_refunds_invoice_id", table_name="finance_billing_refunds"
    )
    op.drop_table("finance_billing_refunds")

    op.drop_index(
        "ix_service_requests_completion_confirmed_by_user_id",
        table_name="service_requests",
    )
    op.drop_constraint(
        "fk_service_requests_completion_confirmed_by_user_id",
        "service_requests",
        type_="foreignkey",
    )
    op.drop_column("service_requests", "completion_confirmed_by_user_id")
    op.drop_column("service_requests", "completion_confirmed_at")
