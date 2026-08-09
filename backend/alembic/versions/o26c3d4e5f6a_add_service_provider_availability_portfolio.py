"""add service provider availability and portfolio stages

Revision ID: o26c3d4e5f6a
Revises: n26b2c3d4e5f
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "o26c3d4e5f6a"
down_revision: str | None = "n26b2c3d4e5f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "service_provider_profiles",
        sa.Column(
            "accepting_requests",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.add_column(
        "service_provider_profiles",
        sa.Column(
            "availability_status",
            sa.String(length=30),
            nullable=False,
            server_default="available",
        ),
    )
    op.add_column(
        "service_provider_profiles",
        sa.Column("typical_response_minutes", sa.Integer(), nullable=True),
    )
    op.create_check_constraint(
        "ck_service_provider_profiles_availability_status",
        "service_provider_profiles",
        "availability_status IN ('available', 'busy', 'unavailable')",
    )
    op.create_check_constraint(
        "ck_service_provider_profiles_response_minutes",
        "service_provider_profiles",
        "typical_response_minutes IS NULL OR "
        "(typical_response_minutes >= 1 AND typical_response_minutes <= 43200)",
    )
    op.add_column(
        "service_offer_media",
        sa.Column("portfolio_stage", sa.String(length=20), nullable=True),
    )
    op.create_check_constraint(
        "ck_service_offer_media_portfolio_stage",
        "service_offer_media",
        "portfolio_stage IS NULL OR portfolio_stage IN ('before', 'after')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_service_offer_media_portfolio_stage",
        "service_offer_media",
        type_="check",
    )
    op.drop_column("service_offer_media", "portfolio_stage")
    op.drop_constraint(
        "ck_service_provider_profiles_response_minutes",
        "service_provider_profiles",
        type_="check",
    )
    op.drop_constraint(
        "ck_service_provider_profiles_availability_status",
        "service_provider_profiles",
        type_="check",
    )
    op.drop_column("service_provider_profiles", "typical_response_minutes")
    op.drop_column("service_provider_profiles", "availability_status")
    op.drop_column("service_provider_profiles", "accepting_requests")
