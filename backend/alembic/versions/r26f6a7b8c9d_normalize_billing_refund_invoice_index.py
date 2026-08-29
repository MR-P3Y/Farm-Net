"""normalize billing refund invoice index

Revision ID: r26f6a7b8c9d
Revises: q26e5f6a7b8c
"""

from collections.abc import Sequence

from alembic import op


revision: str = "r26f6a7b8c9d"
down_revision: str | None = "q26e5f6a7b8c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # q26 created both an anonymous unique index and a redundant non-unique
    # index for invoice_id. Keep the foreign-key-supporting unique index and
    # normalize its name to the SQLAlchemy metadata contract.
    op.drop_index(
        "ix_finance_billing_refunds_invoice_id",
        table_name="finance_billing_refunds",
    )
    op.execute(
        "ALTER TABLE finance_billing_refunds "
        "RENAME INDEX invoice_id TO ix_finance_billing_refunds_invoice_id"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE finance_billing_refunds "
        "RENAME INDEX ix_finance_billing_refunds_invoice_id TO invoice_id"
    )
    op.create_index(
        "ix_finance_billing_refunds_invoice_id",
        "finance_billing_refunds",
        ["invoice_id"],
        unique=False,
    )
