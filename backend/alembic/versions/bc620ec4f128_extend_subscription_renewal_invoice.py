"""extend subscription renewal invoice

Revision ID: bc620ec4f128
Revises: 7b98f2da6a10
Create Date: 2026-07-26 02:30:00
"""

from collections.abc import Sequence

from alembic import op


revision: str = "bc620ec4f128"
down_revision: str | Sequence[str] | None = "7b98f2da6a10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_billing_invoice_platform_owner",
        "finance_billing_invoices",
        type_="check",
    )
    op.create_check_constraint(
        "ck_billing_invoice_platform_owner",
        "finance_billing_invoices",
        "(source_type IN ('platform_subscription', 'platform_subscription_renewal') "
        "AND provider_user_id IS NULL AND provider_amount = 0 "
        "AND platform_amount = total_amount) OR "
        "(source_type NOT IN ('platform_subscription', 'platform_subscription_renewal') "
        "AND provider_user_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_billing_invoice_platform_owner",
        "finance_billing_invoices",
        type_="check",
    )
    op.create_check_constraint(
        "ck_billing_invoice_platform_owner",
        "finance_billing_invoices",
        "(source_type = 'platform_subscription' AND provider_user_id IS NULL "
        "AND provider_amount = 0 AND platform_amount = total_amount) OR "
        "(source_type <> 'platform_subscription' AND provider_user_id IS NOT NULL)",
    )
