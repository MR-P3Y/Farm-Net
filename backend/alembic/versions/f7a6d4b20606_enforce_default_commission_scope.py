"""enforce one default commission policy per source

Revision ID: f7a6d4b20606
Revises: e6f5c3a20505
Create Date: 2026-07-20 00:50:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "f7a6d4b20606"
down_revision: str | Sequence[str] | None = "e6f5c3a20505"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "finance_commission_policies",
        sa.Column("default_scope", sa.String(50), nullable=True),
    )
    op.create_unique_constraint(
        "uq_commission_policy_default_scope",
        "finance_commission_policies",
        ["default_scope"],
    )
    op.create_check_constraint(
        "ck_commission_policy_default_scope",
        "finance_commission_policies",
        "(is_default = 0 AND default_scope IS NULL) OR "
        "(is_default = 1 AND default_scope = source_type)",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_commission_policy_default_scope",
        "finance_commission_policies",
        type_="check",
    )
    op.drop_constraint(
        "uq_commission_policy_default_scope",
        "finance_commission_policies",
        type_="unique",
    )
    op.drop_column("finance_commission_policies", "default_scope")
