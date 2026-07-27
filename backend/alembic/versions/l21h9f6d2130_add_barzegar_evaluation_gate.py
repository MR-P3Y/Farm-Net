"""add Barzegar offline evaluation release gate

Revision ID: l21h9f6d2130
Revises: k21g8e5c1029
Create Date: 2026-07-28 05:20:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "l21h9f6d2130"
down_revision: str | Sequence[str] | None = "k21g8e5c1029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_evaluation_suites",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("suite_key", sa.String(100), nullable=False),
        sa.Column("version", sa.String(80), nullable=False),
        sa.Column("title", sa.String(250), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("active_scope", sa.String(100), nullable=True),
        sa.Column("minimum_pass_rate", sa.Numeric(5, 4), nullable=False),
        sa.Column("created_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("status IN ('draft','active','retired')", name="ck_ai_eval_suite_status"),
        sa.CheckConstraint(
            "minimum_pass_rate BETWEEN 0.5 AND 1", name="ck_ai_eval_suite_minimum_rate"
        ),
        sa.CheckConstraint(
            "(status = 'active' AND active_scope IS NOT NULL) OR "
            "(status <> 'active' AND active_scope IS NULL)",
            name="ck_ai_eval_suite_active_scope",
        ),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("suite_key", "version", name="uq_ai_eval_suite_version"),
        sa.UniqueConstraint("active_scope"),
    )
    op.create_table(
        "ai_evaluation_cases",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("suite_id", sa.BigInteger(), nullable=False),
        sa.Column("case_key", sa.String(100), nullable=False),
        sa.Column("request_kind", sa.String(30), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("required_terms", sa.JSON(), nullable=False),
        sa.Column("forbidden_terms", sa.JSON(), nullable=False),
        sa.Column("requires_uncertainty", sa.Boolean(), nullable=False),
        sa.Column("requires_human_review", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "request_kind IN ('text','farm_context','deep_analysis','image_analysis',"
            "'smart_diary','report')",
            name="ck_ai_eval_case_kind",
        ),
        sa.ForeignKeyConstraint(["suite_id"], ["ai_evaluation_suites.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("suite_id", "case_key", name="uq_ai_eval_case_suite_key"),
    )
    op.create_table(
        "ai_evaluation_runs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("suite_id", sa.BigInteger(), nullable=False),
        sa.Column("idempotency_key", sa.String(180), nullable=False),
        sa.Column("model_configuration_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("total_cases", sa.Integer(), nullable=False),
        sa.Column("passed_cases", sa.Integer(), nullable=False),
        sa.Column("pass_rate", sa.Numeric(5, 4), nullable=False),
        sa.Column("release_passed", sa.Boolean(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("status IN ('completed')", name="ck_ai_eval_run_status"),
        sa.CheckConstraint(
            "total_cases > 0 AND passed_cases BETWEEN 0 AND total_cases",
            name="ck_ai_eval_run_counts",
        ),
        sa.CheckConstraint("pass_rate BETWEEN 0 AND 1", name="ck_ai_eval_run_rate"),
        sa.ForeignKeyConstraint(
            ["model_configuration_id"], ["ai_model_configurations.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["suite_id"], ["ai_evaluation_suites.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_table(
        "ai_evaluation_results",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.BigInteger(), nullable=False),
        sa.Column("case_id", sa.BigInteger(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("failure_codes", sa.JSON(), nullable=False),
        sa.Column("output_sha256", sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["ai_evaluation_cases.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["run_id"], ["ai_evaluation_runs.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "case_id", name="uq_ai_eval_result_run_case"),
    )


def downgrade() -> None:
    op.drop_table("ai_evaluation_results")
    op.drop_table("ai_evaluation_runs")
    op.drop_table("ai_evaluation_cases")
    op.drop_table("ai_evaluation_suites")
