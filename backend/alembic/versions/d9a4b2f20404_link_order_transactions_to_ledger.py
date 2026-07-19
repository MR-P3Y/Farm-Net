"""link order financial transactions to ledger journals

Revision ID: d9a4b2f20404
Revises: c7e8a1f20303
Create Date: 2026-07-19 23:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "d9a4b2f20404"
down_revision: str | Sequence[str] | None = "c7e8a1f20303"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "finance_ledger_transactions",
        sa.Column("legacy_transaction_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_ledger_legacy_transaction",
        "finance_ledger_transactions",
        "finance_transactions",
        ["legacy_transaction_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_finance_ledger_transactions_legacy_transaction_id",
        "finance_ledger_transactions",
        ["legacy_transaction_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_ledger_transactions_legacy_transaction_id",
        table_name="finance_ledger_transactions",
    )
    op.drop_constraint(
        "fk_ledger_legacy_transaction",
        "finance_ledger_transactions",
        type_="foreignkey",
    )
    op.drop_column("finance_ledger_transactions", "legacy_transaction_id")
