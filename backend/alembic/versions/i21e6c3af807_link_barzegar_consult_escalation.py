"""link Barzegar safety escalation to consult requests

Revision ID: i21e6c3af807
Revises: h21d5b29e7f6
Create Date: 2026-07-28 01:35:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "i21e6c3af807"
down_revision: str | Sequence[str] | None = "h21d5b29e7f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ai_requests", sa.Column("consult_request_id", sa.BigInteger(), nullable=True)
    )
    op.create_unique_constraint(
        "uq_ai_requests_consult_request", "ai_requests", ["consult_request_id"]
    )
    op.create_foreign_key(
        "fk_ai_requests_consult_request",
        "ai_requests",
        "consult_requests",
        ["consult_request_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_ai_requests_consult_request", "ai_requests", type_="foreignkey"
    )
    op.drop_constraint(
        "uq_ai_requests_consult_request", "ai_requests", type_="unique"
    )
    op.drop_column("ai_requests", "consult_request_id")
