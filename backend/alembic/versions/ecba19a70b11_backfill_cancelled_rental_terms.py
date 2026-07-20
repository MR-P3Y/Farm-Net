"""backfill cancelled accepted rental financial terms

Revision ID: ecba19a70b11
Revises: dbea08f60a10
"""

from collections.abc import Sequence

from alembic import op

revision: str = "ecba19a70b11"
down_revision: str | None = "dbea08f60a10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO finance_rental_terms (
            rental_request_id, payer_user_id, provider_user_id,
            pricing_rule_id_snapshot, requested_units_snapshot,
            unit_price_snapshot, rental_revenue_amount,
            deposit_principal_amount, funding_total_amount, currency, status,
            accepted_at, cancelled_at, created_at, updated_at
        )
        SELECT
            rr.id, rr.requester_user_id, lp.user_id,
            rr.pricing_rule_id, rr.requested_units,
            rr.price_per_unit_snapshot, rr.rental_amount_snapshot,
            rr.deposit_amount_snapshot, rr.total_amount_snapshot, rr.currency,
            'cancelled_unfunded', COALESCE(rr.accepted_at, rr.created_at),
            COALESCE(rr.cancelled_at, rr.updated_at),
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        FROM rental_requests rr
        JOIN rental_lessor_profiles lp ON lp.id = rr.lessor_profile_id
        LEFT JOIN finance_rental_terms ft ON ft.rental_request_id = rr.id
        WHERE rr.status = 'cancelled'
          AND ft.id IS NULL
          AND rr.price_per_unit_snapshot IS NOT NULL
          AND rr.rental_amount_snapshot > 0
          AND rr.deposit_amount_snapshot >= 0
          AND rr.total_amount_snapshot =
              rr.rental_amount_snapshot + rr.deposit_amount_snapshot
          AND rr.currency = 'TOMAN'
        """
    )


def downgrade() -> None:
    # Historical accepted terms are retained; downgrade never deletes finance history.
    pass
