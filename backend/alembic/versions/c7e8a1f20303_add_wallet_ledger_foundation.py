"""add wallet account and double-entry ledger foundation

Revision ID: c7e8a1f20303
Revises: 4c9a2f20b102
Create Date: 2026-07-19 22:10:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "c7e8a1f20303"
down_revision: str | Sequence[str] | None = "4c9a2f20b102"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "finance_wallet_accounts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=True),
        sa.Column("account_code", sa.String(length=100), nullable=False),
        sa.Column("account_kind", sa.String(length=30), nullable=False),
        sa.Column("purpose", sa.String(length=50), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("currency = 'TOMAN'", name="ck_wallet_accounts_currency_toman"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_code"),
        sa.UniqueConstraint(
            "owner_user_id", "purpose", "currency", name="uq_wallet_owner_purpose_currency"
        ),
    )
    op.create_index(
        "ix_wallet_accounts_owner_status",
        "finance_wallet_accounts",
        ["owner_user_id", "status"],
    )
    op.create_index(
        op.f("ix_finance_wallet_accounts_account_kind"),
        "finance_wallet_accounts",
        ["account_kind"],
    )
    op.create_index(
        op.f("ix_finance_wallet_accounts_owner_user_id"),
        "finance_wallet_accounts",
        ["owner_user_id"],
    )
    op.create_index(
        op.f("ix_finance_wallet_accounts_purpose"),
        "finance_wallet_accounts",
        ["purpose"],
    )
    op.create_index(
        op.f("ix_finance_wallet_accounts_status"),
        "finance_wallet_accounts",
        ["status"],
    )

    op.create_table(
        "finance_ledger_transactions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("journal_number", sa.String(length=60), nullable=False),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("total_debit", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_credit", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("reversal_of_id", sa.BigInteger(), nullable=True),
        sa.Column("actor_user_id", sa.BigInteger(), nullable=True),
        sa.Column("trace_id", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("posted_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("currency = 'TOMAN'", name="ck_ledger_transactions_currency_toman"),
        sa.CheckConstraint("total_debit > 0", name="ck_ledger_transactions_debit_positive"),
        sa.CheckConstraint("total_credit > 0", name="ck_ledger_transactions_credit_positive"),
        sa.CheckConstraint(
            "total_debit = total_credit", name="ck_ledger_transactions_balanced_totals"
        ),
        sa.ForeignKeyConstraint(["actor_user_id"], ["auth_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["reversal_of_id"], ["finance_ledger_transactions.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
        sa.UniqueConstraint("journal_number"),
        sa.UniqueConstraint("reversal_of_id", name="uq_ledger_transaction_reversal"),
    )
    op.create_index(
        "ix_ledger_transactions_posted",
        "finance_ledger_transactions",
        ["posted_at", "id"],
    )
    op.create_index(
        "ix_ledger_transactions_source",
        "finance_ledger_transactions",
        ["source_type", "source_id"],
    )
    for column in (
        "actor_user_id",
        "event_type",
        "reversal_of_id",
        "source_type",
        "status",
        "trace_id",
    ):
        op.create_index(
            op.f(f"ix_finance_ledger_transactions_{column}"),
            "finance_ledger_transactions",
            [column],
        )

    op.create_table(
        "finance_ledger_entries",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("transaction_id", sa.BigInteger(), nullable=False),
        sa.Column("account_id", sa.BigInteger(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("memo", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_ledger_entries_amount_positive"),
        sa.CheckConstraint("currency = 'TOMAN'", name="ck_ledger_entries_currency_toman"),
        sa.CheckConstraint("sequence > 0", name="ck_ledger_entries_sequence_positive"),
        sa.CheckConstraint("side IN ('debit', 'credit')", name="ck_ledger_entries_side"),
        sa.ForeignKeyConstraint(
            ["account_id"], ["finance_wallet_accounts.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["transaction_id"], ["finance_ledger_transactions.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id", "sequence", name="uq_ledger_entry_sequence"),
    )
    op.create_index(
        "ix_ledger_entries_account_created",
        "finance_ledger_entries",
        ["account_id", "created_at"],
    )
    for column in ("account_id", "side", "transaction_id"):
        op.create_index(
            op.f(f"ix_finance_ledger_entries_{column}"),
            "finance_ledger_entries",
            [column],
        )


def downgrade() -> None:
    op.drop_table("finance_ledger_entries")
    op.drop_table("finance_ledger_transactions")
    op.drop_table("finance_wallet_accounts")
