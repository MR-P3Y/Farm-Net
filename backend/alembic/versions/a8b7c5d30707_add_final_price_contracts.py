"""add service and consultation final price contracts

Revision ID: a8b7c5d30707
Revises: f7a6d4b20606
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "a8b7c5d30707"
down_revision: str | None = "f7a6d4b20606"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "finance_final_price_proposals",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payer_user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider_user_id", sa.BigInteger(), nullable=False),
        sa.Column("proposed_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("description_snapshot", sa.String(500), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("active_scope", sa.String(120), nullable=True),
        sa.Column("accepted_scope", sa.String(120), nullable=True),
        sa.Column("decided_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("proposed_at", sa.DateTime(), nullable=False),
        sa.Column("decided_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_final_price_amount_positive"),
        sa.CheckConstraint("currency = 'TOMAN'", name="ck_final_price_currency_toman"),
        sa.CheckConstraint(
            "(status = 'proposed' AND active_scope IS NOT NULL) OR "
            "(status <> 'proposed' AND active_scope IS NULL)",
            name="ck_final_price_active_scope",
        ),
        sa.CheckConstraint(
            "(status = 'accepted' AND accepted_scope IS NOT NULL) OR "
            "(status <> 'accepted' AND accepted_scope IS NULL)",
            name="ck_final_price_accepted_scope",
        ),
        sa.ForeignKeyConstraint(["payer_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["provider_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["proposed_by_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["decided_by_user_id"], ["auth_users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("active_scope", name="uq_finance_final_price_proposals_active_scope"),
        sa.UniqueConstraint("accepted_scope", name="uq_finance_final_price_proposals_accepted_scope"),
        sa.UniqueConstraint(
            "source_type", "source_id", "version", name="uq_final_price_source_version"
        ),
    )
    for column in (
        "payer_user_id",
        "provider_user_id",
        "proposed_by_user_id",
        "decided_by_user_id",
        "status",
    ):
        op.create_index(
            op.f(f"ix_finance_final_price_proposals_{column}"),
            "finance_final_price_proposals",
            [column],
        )
    op.create_index(
        "ix_final_price_source",
        "finance_final_price_proposals",
        ["source_type", "source_id", "version"],
    )
    op.create_index(
        "ix_final_price_payer_status",
        "finance_final_price_proposals",
        ["payer_user_id", "status"],
    )
    op.create_index(
        "ix_final_price_provider_status",
        "finance_final_price_proposals",
        ["provider_user_id", "status"],
    )


def downgrade() -> None:
    op.drop_table("finance_final_price_proposals")
