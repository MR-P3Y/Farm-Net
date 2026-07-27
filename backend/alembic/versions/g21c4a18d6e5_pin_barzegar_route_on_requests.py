"""pin Barzegar route versions on requests and attempts

Revision ID: g21c4a18d6e5
Revises: f21b9c37a4d2
Create Date: 2026-07-27 22:05:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "g21c4a18d6e5"
down_revision: str | Sequence[str] | None = "f21b9c37a4d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ai_requests", sa.Column("routing_policy_version", sa.String(length=80), nullable=True)
    )
    op.execute(
        "UPDATE ai_requests SET routing_policy_version = 'routing-v1' "
        "WHERE routing_policy_version IS NULL"
    )
    op.alter_column(
        "ai_requests",
        "routing_policy_version",
        existing_type=sa.String(length=80),
        nullable=False,
    )
    op.add_column(
        "ai_execution_attempts",
        sa.Column("model_configuration_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "ai_execution_attempts",
        sa.Column("routing_policy_version", sa.String(length=80), nullable=True),
    )
    op.create_foreign_key(
        "fk_ai_attempt_model_configuration",
        "ai_execution_attempts",
        "ai_model_configurations",
        ["model_configuration_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_ai_attempt_model_configuration", "ai_execution_attempts", type_="foreignkey"
    )
    op.drop_column("ai_execution_attempts", "routing_policy_version")
    op.drop_column("ai_execution_attempts", "model_configuration_id")
    op.drop_column("ai_requests", "routing_policy_version")
