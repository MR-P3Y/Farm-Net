"""add service provider service area

Revision ID: d62e2f6b7c11
Revises: c4a8d91e72b1
Create Date: 2026-07-02 00:20:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "d62e2f6b7c11"
down_revision: str | Sequence[str] | None = "c4a8d91e72b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "service_provider_profiles",
        sa.Column("service_area", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("service_provider_profiles", "service_area")
