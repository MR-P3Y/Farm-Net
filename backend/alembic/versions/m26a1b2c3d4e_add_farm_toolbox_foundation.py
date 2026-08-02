"""add Farm toolbox calculations finance and plans

Revision ID: m26a1b2c3d4e
Revises: l21h9f6d2130
Create Date: 2026-08-02 03:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "m26a1b2c3d4e"
down_revision: str | Sequence[str] | None = "l21h9f6d2130"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "farm_tool_calculations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("farm_id", sa.BigInteger(), nullable=False),
        sa.Column("plot_id", sa.BigInteger(), nullable=True),
        sa.Column("cycle_id", sa.BigInteger(), nullable=True),
        sa.Column("calculator_type", sa.String(40), nullable=False),
        sa.Column("formula_version", sa.String(30), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("inputs_json", sa.JSON(), nullable=False),
        sa.Column("results_json", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "calculator_type IN "
            "('seed','irrigation','fertilizer','spraying','cost_profit',"
            "'unit_conversion','pump_fuel')",
            name="ck_farm_tool_calculations_type",
        ),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["plot_id"], ["farm_plots.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["cycle_id"], ["farm_crop_cycles.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_farm_tool_calculations_farm_id",
        "farm_tool_calculations",
        ["farm_id"],
    )
    op.create_index(
        "ix_farm_tool_calculations_plot_id",
        "farm_tool_calculations",
        ["plot_id"],
    )
    op.create_index(
        "ix_farm_tool_calculations_cycle_id",
        "farm_tool_calculations",
        ["cycle_id"],
    )
    op.create_index(
        "ix_farm_tool_calculations_farm_created",
        "farm_tool_calculations",
        ["farm_id", "created_at"],
    )
    op.create_index(
        "ix_farm_tool_calculations_plot_type_created",
        "farm_tool_calculations",
        ["plot_id", "calculator_type", "created_at"],
    )

    op.create_table(
        "farm_financial_entries",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("farm_id", sa.BigInteger(), nullable=False),
        sa.Column("plot_id", sa.BigInteger(), nullable=True),
        sa.Column("cycle_id", sa.BigInteger(), nullable=True),
        sa.Column("entry_type", sa.String(20), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("amount_toman", sa.Numeric(18, 2), nullable=False),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("voided_at", sa.DateTime(), nullable=True),
        sa.Column("void_reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "entry_type IN ('expense','revenue')", name="ck_farm_financial_type"
        ),
        sa.CheckConstraint(
            "category IN ('seed','irrigation','fertilizer','pesticide','labor',"
            "'fuel','machinery','harvest_sale','other')",
            name="ck_farm_financial_category",
        ),
        sa.CheckConstraint(
            "amount_toman > 0", name="ck_farm_financial_amount_positive"
        ),
        sa.CheckConstraint(
            "(voided_at IS NULL AND void_reason IS NULL) OR "
            "(voided_at IS NOT NULL AND void_reason IS NOT NULL)",
            name="ck_farm_financial_void_state",
        ),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["plot_id"], ["farm_plots.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["cycle_id"], ["farm_crop_cycles.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_farm_financial_entries_farm_id", "farm_financial_entries", ["farm_id"]
    )
    op.create_index(
        "ix_farm_financial_entries_plot_id", "farm_financial_entries", ["plot_id"]
    )
    op.create_index(
        "ix_farm_financial_entries_cycle_id", "farm_financial_entries", ["cycle_id"]
    )
    op.create_index(
        "ix_farm_financial_entries_farm_date_type",
        "farm_financial_entries",
        ["farm_id", "occurred_on", "entry_type"],
    )

    op.create_table(
        "farm_plan_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("farm_id", sa.BigInteger(), nullable=False),
        sa.Column("plot_id", sa.BigInteger(), nullable=True),
        sa.Column("cycle_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("planned_for", sa.Date(), nullable=False),
        sa.Column("reminder_at", sa.DateTime(), nullable=True),
        sa.Column("reminder_sent_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("cancel_reason", sa.String(500), nullable=True),
        sa.Column("farm_operation_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "operation_type IN "
            "('land_preparation','planting','irrigation','fertilizing','spraying',"
            "'weeding','pruning','monitoring','other')",
            name="ck_farm_plan_items_operation_type",
        ),
        sa.CheckConstraint(
            "status IN ('planned','completed','cancelled')",
            name="ck_farm_plan_items_status",
        ),
        sa.CheckConstraint(
            "(status = 'planned' AND completed_at IS NULL AND cancelled_at IS NULL "
            "AND cancel_reason IS NULL AND farm_operation_id IS NULL) OR "
            "(status = 'completed' AND completed_at IS NOT NULL AND cancelled_at IS NULL "
            "AND cancel_reason IS NULL) OR "
            "(status = 'cancelled' AND completed_at IS NULL AND cancelled_at IS NOT NULL "
            "AND farm_operation_id IS NULL)",
            name="ck_farm_plan_items_lifecycle",
        ),
        sa.CheckConstraint(
            "reminder_sent_at IS NULL OR reminder_at IS NOT NULL",
            name="ck_farm_plan_items_reminder_state",
        ),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["plot_id"], ["farm_plots.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["cycle_id"], ["farm_crop_cycles.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["farm_operation_id"], ["farm_operations.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "farm_operation_id", name="uq_farm_plan_items_farm_operation"
        ),
    )
    op.create_index("ix_farm_plan_items_farm_id", "farm_plan_items", ["farm_id"])
    op.create_index("ix_farm_plan_items_plot_id", "farm_plan_items", ["plot_id"])
    op.create_index("ix_farm_plan_items_cycle_id", "farm_plan_items", ["cycle_id"])
    op.create_index(
        "ix_farm_plan_items_farm_status_date",
        "farm_plan_items",
        ["farm_id", "status", "planned_for"],
    )
    op.create_index(
        "ix_farm_plan_items_reminder_due",
        "farm_plan_items",
        ["status", "reminder_at", "reminder_sent_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_farm_plan_items_reminder_due", table_name="farm_plan_items")
    op.drop_index("ix_farm_plan_items_farm_status_date", table_name="farm_plan_items")
    op.drop_index("ix_farm_plan_items_cycle_id", table_name="farm_plan_items")
    op.drop_index("ix_farm_plan_items_plot_id", table_name="farm_plan_items")
    op.drop_index("ix_farm_plan_items_farm_id", table_name="farm_plan_items")
    op.drop_table("farm_plan_items")

    op.drop_index(
        "ix_farm_financial_entries_farm_date_type", table_name="farm_financial_entries"
    )
    op.drop_index("ix_farm_financial_entries_cycle_id", table_name="farm_financial_entries")
    op.drop_index("ix_farm_financial_entries_plot_id", table_name="farm_financial_entries")
    op.drop_index("ix_farm_financial_entries_farm_id", table_name="farm_financial_entries")
    op.drop_table("farm_financial_entries")

    op.drop_index(
        "ix_farm_tool_calculations_plot_type_created",
        table_name="farm_tool_calculations",
    )
    op.drop_index(
        "ix_farm_tool_calculations_farm_created", table_name="farm_tool_calculations"
    )
    op.drop_index("ix_farm_tool_calculations_cycle_id", table_name="farm_tool_calculations")
    op.drop_index("ix_farm_tool_calculations_plot_id", table_name="farm_tool_calculations")
    op.drop_index("ix_farm_tool_calculations_farm_id", table_name="farm_tool_calculations")
    op.drop_table("farm_tool_calculations")
