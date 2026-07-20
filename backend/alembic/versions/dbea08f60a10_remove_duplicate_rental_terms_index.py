"""remove duplicate rental terms unique index

Revision ID: dbea08f60a10
Revises: cad9e7f50909
"""

from collections.abc import Sequence

from alembic import op

revision: str = "dbea08f60a10"
down_revision: str | None = "cad9e7f50909"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("rental_request_id", table_name="finance_rental_terms")


def downgrade() -> None:
    op.create_index(
        "rental_request_id",
        "finance_rental_terms",
        ["rental_request_id"],
        unique=True,
    )
