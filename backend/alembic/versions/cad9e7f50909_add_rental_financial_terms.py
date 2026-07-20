"""add rental revenue and deposit financial terms

Revision ID: cad9e7f50909
Revises: b9c8d6e40808
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "cad9e7f50909"
down_revision: str | None = "b9c8d6e40808"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "finance_rental_terms",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("rental_request_id", sa.BigInteger(), nullable=False),
        sa.Column("payer_user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider_user_id", sa.BigInteger(), nullable=False),
        sa.Column("pricing_rule_id_snapshot", sa.BigInteger(), nullable=False),
        sa.Column("requested_units_snapshot", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit_price_snapshot", sa.Numeric(18, 2), nullable=False),
        sa.Column("rental_revenue_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("deposit_principal_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("funding_total_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("accepted_at", sa.DateTime(), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("operationally_completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("requested_units_snapshot > 0", name="ck_rental_terms_units_positive"),
        sa.CheckConstraint("unit_price_snapshot > 0", name="ck_rental_terms_unit_price_positive"),
        sa.CheckConstraint("rental_revenue_amount > 0", name="ck_rental_terms_revenue_positive"),
        sa.CheckConstraint(
            "deposit_principal_amount >= 0", name="ck_rental_terms_deposit_nonnegative"
        ),
        sa.CheckConstraint(
            "funding_total_amount = rental_revenue_amount + deposit_principal_amount",
            name="ck_rental_terms_total_components",
        ),
        sa.CheckConstraint("currency = 'TOMAN'", name="ck_rental_terms_currency_toman"),
        sa.CheckConstraint(
            "status IN ('unfunded', 'cancelled_unfunded', "
            "'operationally_completed_unfunded')",
            name="ck_rental_terms_status",
        ),
        sa.ForeignKeyConstraint(
            ["rental_request_id"], ["rental_requests.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["payer_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["provider_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rental_request_id"),
    )
    for column in ("rental_request_id", "payer_user_id", "provider_user_id", "status"):
        op.create_index(
            op.f(f"ix_finance_rental_terms_{column}"),
            "finance_rental_terms",
            [column],
            unique=column == "rental_request_id",
        )
    op.create_index(
        "ix_rental_terms_payer_status",
        "finance_rental_terms",
        ["payer_user_id", "status"],
    )
    op.create_index(
        "ix_rental_terms_provider_status",
        "finance_rental_terms",
        ["provider_user_id", "status"],
    )
    op.execute(
        """
        INSERT INTO finance_rental_terms (
            rental_request_id, payer_user_id, provider_user_id,
            pricing_rule_id_snapshot, requested_units_snapshot,
            unit_price_snapshot, rental_revenue_amount,
            deposit_principal_amount, funding_total_amount, currency, status,
            accepted_at, operationally_completed_at, created_at, updated_at
        )
        SELECT
            rr.id, rr.requester_user_id, lp.user_id,
            rr.pricing_rule_id, rr.requested_units,
            rr.price_per_unit_snapshot, rr.rental_amount_snapshot,
            rr.deposit_amount_snapshot, rr.total_amount_snapshot, rr.currency,
            CASE WHEN rr.status = 'completed'
                THEN 'operationally_completed_unfunded' ELSE 'unfunded' END,
            COALESCE(rr.accepted_at, rr.created_at),
            CASE WHEN rr.status = 'completed'
                THEN COALESCE(rr.completed_at, rr.updated_at) ELSE NULL END,
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        FROM rental_requests rr
        JOIN rental_lessor_profiles lp ON lp.id = rr.lessor_profile_id
        WHERE rr.status IN ('accepted', 'in_progress', 'completed')
          AND rr.price_per_unit_snapshot IS NOT NULL
          AND rr.rental_amount_snapshot > 0
          AND rr.deposit_amount_snapshot >= 0
          AND rr.total_amount_snapshot =
              rr.rental_amount_snapshot + rr.deposit_amount_snapshot
          AND rr.currency = 'TOMAN'
        """
    )


def downgrade() -> None:
    op.drop_table("finance_rental_terms")
