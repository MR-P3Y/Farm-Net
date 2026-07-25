"""harden subscription audit and concurrency

Revision ID: e17c4b82a6d9
Revises: d8f3a9c21b74
Create Date: 2026-07-26 14:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "e17c4b82a6d9"
down_revision: str | Sequence[str] | None = "d8f3a9c21b74"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "billing_plans",
        sa.Column(
            "active_code",
            sa.String(length=80),
            sa.Computed(
                "CASE WHEN status = 'active' THEN code ELSE NULL END",
                persisted=True,
            ),
            nullable=True,
        ),
    )
    op.create_unique_constraint(
        "uq_billing_plan_one_active_code", "billing_plans", ["active_code"]
    )
    op.add_column(
        "billing_subscriptions",
        sa.Column(
            "current_user_id",
            sa.BigInteger(),
            sa.Computed(
                "CASE WHEN status IN ('active', 'grace') THEN user_id ELSE NULL END",
                persisted=True,
            ),
            nullable=True,
        ),
    )
    op.create_unique_constraint(
        "uq_billing_subscription_one_current_user",
        "billing_subscriptions",
        ["current_user_id"],
    )
    op.create_table(
        "billing_audit_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("event_key", sa.String(length=180), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=40), nullable=False),
        sa.Column("target_id", sa.BigInteger(), nullable=False),
        sa.Column("subscription_id", sa.BigInteger(), nullable=True),
        sa.Column("plan_id", sa.BigInteger(), nullable=True),
        sa.Column("actor_type", sa.String(length=20), nullable=False),
        sa.Column("actor_user_id", sa.BigInteger(), nullable=True),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("old_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("trace_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "actor_type IN ('user', 'admin', 'system')",
            name="ck_billing_audit_actor_type",
        ),
        sa.CheckConstraint(
            "target_type IN ('plan', 'subscription', 'payment', 'quota')",
            name="ck_billing_audit_target_type",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"], ["auth_users.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"], ["billing_plans.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["billing_subscriptions.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_key"),
    )
    op.create_index(
        "ix_billing_audit_logs_action",
        "billing_audit_logs",
        ["action"],
        unique=False,
    )
    op.create_index(
        "ix_billing_audit_logs_actor_user_id",
        "billing_audit_logs",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_billing_audit_logs_plan_id",
        "billing_audit_logs",
        ["plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_billing_audit_logs_subscription_id",
        "billing_audit_logs",
        ["subscription_id"],
        unique=False,
    )
    op.create_index(
        "ix_billing_audit_logs_target_id",
        "billing_audit_logs",
        ["target_id"],
        unique=False,
    )
    op.create_index(
        "ix_billing_audit_logs_target_type",
        "billing_audit_logs",
        ["target_type"],
        unique=False,
    )
    op.create_index(
        "ix_billing_audit_logs_trace_id",
        "billing_audit_logs",
        ["trace_id"],
        unique=False,
    )
    op.create_index(
        "ix_billing_audit_target_created",
        "billing_audit_logs",
        ["target_type", "target_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_billing_audit_target_created", table_name="billing_audit_logs")
    op.drop_index("ix_billing_audit_logs_trace_id", table_name="billing_audit_logs")
    op.drop_index("ix_billing_audit_logs_target_type", table_name="billing_audit_logs")
    op.drop_index("ix_billing_audit_logs_target_id", table_name="billing_audit_logs")
    op.drop_index(
        "ix_billing_audit_logs_subscription_id", table_name="billing_audit_logs"
    )
    op.drop_index("ix_billing_audit_logs_plan_id", table_name="billing_audit_logs")
    op.drop_index(
        "ix_billing_audit_logs_actor_user_id", table_name="billing_audit_logs"
    )
    op.drop_index("ix_billing_audit_logs_action", table_name="billing_audit_logs")
    op.drop_table("billing_audit_logs")
    op.drop_constraint(
        "uq_billing_subscription_one_current_user",
        "billing_subscriptions",
        type_="unique",
    )
    op.drop_column("billing_subscriptions", "current_user_id")
    op.drop_constraint(
        "uq_billing_plan_one_active_code", "billing_plans", type_="unique"
    )
    op.drop_column("billing_plans", "active_code")
