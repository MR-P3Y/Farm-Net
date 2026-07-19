"""canonicalize consultation currency to Iranian toman

Revision ID: 4c9a2f20b102
Revises: 104ae669cc1a
Create Date: 2026-07-19 21:30:00
"""

from collections.abc import Sequence

from alembic import op


revision: str = "4c9a2f20b102"
down_revision: str | Sequence[str] | None = "104ae669cc1a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE consult_requests
        SET budget_amount = CASE
                WHEN budget_amount IS NULL THEN NULL
                ELSE budget_amount / 10
            END,
            currency = 'TOMAN'
        WHERE UPPER(currency) = 'IRR'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE consult_requests
        SET budget_amount = CASE
                WHEN budget_amount IS NULL THEN NULL
                ELSE budget_amount * 10
            END,
            currency = 'IRR'
        WHERE UPPER(currency) = 'TOMAN'
        """
    )
