"""harden final price source and status enums

Revision ID: b9c8d6e40808
Revises: a8b7c5d30707
"""

from collections.abc import Sequence

from alembic import op

revision: str = "b9c8d6e40808"
down_revision: str | None = "a8b7c5d30707"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_final_price_source_type",
        "finance_final_price_proposals",
        "source_type IN ('service_request', 'consultation_request')",
    )
    op.create_check_constraint(
        "ck_final_price_status",
        "finance_final_price_proposals",
        "status IN ('proposed', 'accepted', 'rejected', 'superseded')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_final_price_status", "finance_final_price_proposals", type_="check"
    )
    op.drop_constraint(
        "ck_final_price_source_type", "finance_final_price_proposals", type_="check"
    )
