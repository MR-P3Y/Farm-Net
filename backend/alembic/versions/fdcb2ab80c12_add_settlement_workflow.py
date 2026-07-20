"""add balance release and settlement workflow

Revision ID: fdcb2ab80c12
Revises: ecba19a70b11
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "fdcb2ab80c12"
down_revision: str | None = "ecba19a70b11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "finance_settlement_requests",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("requester_user_id", sa.BigInteger(), nullable=False),
        sa.Column("idempotency_key", sa.String(180), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("reserve_journal_id", sa.BigInteger(), nullable=False),
        sa.Column("decision_journal_id", sa.BigInteger(), nullable=True),
        sa.Column("note", sa.String(500), nullable=True),
        sa.Column("admin_note", sa.String(1000), nullable=True),
        sa.Column("decided_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("requested_at", sa.DateTime(), nullable=False),
        sa.Column("decided_at", sa.DateTime(), nullable=True),
        sa.Column("simulated_completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_settlement_amount_positive"),
        sa.CheckConstraint("currency = 'TOMAN'", name="ck_settlement_currency_toman"),
        sa.CheckConstraint(
            "status IN ('requested', 'approved', 'rejected', 'simulated_completed')",
            name="ck_settlement_status",
        ),
        sa.ForeignKeyConstraint(["requester_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["decided_by_user_id"], ["auth_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["reserve_journal_id"], ["finance_ledger_transactions.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["decision_journal_id"], ["finance_ledger_transactions.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
        sa.UniqueConstraint("reserve_journal_id"),
        sa.UniqueConstraint("decision_journal_id"),
    )
    for column in (
        "requester_user_id",
        "status",
        "decided_by_user_id",
    ):
        op.create_index(
            op.f(f"ix_finance_settlement_requests_{column}"),
            "finance_settlement_requests",
            [column],
        )
    op.create_index(
        "ix_settlement_requester_status",
        "finance_settlement_requests",
        ["requester_user_id", "status"],
    )
    op.create_index(
        "ix_settlement_status_requested",
        "finance_settlement_requests",
        ["status", "requested_at"],
    )


def downgrade() -> None:
    op.drop_table("finance_settlement_requests")
