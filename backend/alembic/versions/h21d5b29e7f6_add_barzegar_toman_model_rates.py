"""add Barzegar TOMAN model rates

Revision ID: h21d5b29e7f6
Revises: g21c4a18d6e5
Create Date: 2026-07-28 00:40:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "h21d5b29e7f6"
down_revision: str | Sequence[str] | None = "g21c4a18d6e5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_ai_usage_cost_pair", "ai_usage_records", type_="check")
    op.alter_column(
        "ai_usage_records",
        "provider_cost_currency",
        existing_type=sa.String(length=3),
        type_=sa.String(length=5),
        existing_nullable=True,
    )
    op.create_check_constraint(
        "ck_ai_usage_cost_pair",
        "ai_usage_records",
        "(provider_cost_amount IS NULL AND provider_cost_currency IS NULL) OR "
        "(provider_cost_amount >= 0 AND provider_cost_currency = 'TOMAN')",
    )
    op.add_column(
        "ai_model_configurations",
        sa.Column("input_cost_per_million_toman", sa.Numeric(18, 4), nullable=True),
    )
    op.add_column(
        "ai_model_configurations",
        sa.Column("cached_input_cost_per_million_toman", sa.Numeric(18, 4), nullable=True),
    )
    op.add_column(
        "ai_model_configurations",
        sa.Column("output_cost_per_million_toman", sa.Numeric(18, 4), nullable=True),
    )
    op.create_check_constraint(
        "ck_ai_model_configuration_toman_rates",
        "ai_model_configurations",
        "(input_cost_per_million_toman IS NULL "
        "AND cached_input_cost_per_million_toman IS NULL "
        "AND output_cost_per_million_toman IS NULL) OR "
        "(input_cost_per_million_toman >= 0 "
        "AND cached_input_cost_per_million_toman >= 0 "
        "AND output_cost_per_million_toman >= 0)",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_ai_model_configuration_toman_rates",
        "ai_model_configurations",
        type_="check",
    )
    op.drop_column("ai_model_configurations", "output_cost_per_million_toman")
    op.drop_column("ai_model_configurations", "cached_input_cost_per_million_toman")
    op.drop_column("ai_model_configurations", "input_cost_per_million_toman")
    op.drop_constraint("ck_ai_usage_cost_pair", "ai_usage_records", type_="check")
    op.alter_column(
        "ai_usage_records",
        "provider_cost_currency",
        existing_type=sa.String(length=5),
        type_=sa.String(length=3),
        existing_nullable=True,
    )
    op.create_check_constraint(
        "ck_ai_usage_cost_pair",
        "ai_usage_records",
        "(provider_cost_amount IS NULL AND provider_cost_currency IS NULL) OR "
        "(provider_cost_amount >= 0 AND CHAR_LENGTH(provider_cost_currency) = 3)",
    )
