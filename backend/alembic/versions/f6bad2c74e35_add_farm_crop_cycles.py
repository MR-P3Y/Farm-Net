"""add farm crop cycles

Revision ID: f6bad2c74e35
Revises: e5a9c1b63d24
Create Date: 2026-07-26 00:40:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "f6bad2c74e35"
down_revision: str | Sequence[str] | None = "e5a9c1b63d24"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "farm_crop_cycles",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("plot_id", sa.BigInteger(), nullable=False),
        sa.Column("crop_id", sa.BigInteger(), nullable=False),
        sa.Column("variety_id", sa.BigInteger(), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=True),
        sa.Column("cultivation_mode", sa.String(length=30), nullable=False),
        sa.Column("planned_start_date", sa.Date(), nullable=False),
        sa.Column("planned_end_date", sa.Date(), nullable=False),
        sa.Column("actual_start_date", sa.Date(), nullable=True),
        sa.Column("actual_end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "actual_end_date IS NULL OR actual_end_date >= actual_start_date",
            name="ck_farm_crop_cycles_actual_dates",
        ),
        sa.CheckConstraint(
            "actual_end_date IS NULL OR actual_start_date IS NOT NULL",
            name="ck_farm_crop_cycles_actual_end_requires_start",
        ),
        sa.CheckConstraint(
            "cultivation_mode in ('single', 'intercrop')",
            name="ck_farm_crop_cycles_cultivation_mode",
        ),
        sa.CheckConstraint(
            "(status = 'planned' AND actual_start_date IS NULL AND actual_end_date IS NULL) OR "
            "(status = 'active' AND actual_start_date IS NOT NULL AND actual_end_date IS NULL) OR "
            "(status = 'completed' AND actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL) OR "
            "(status = 'cancelled' AND actual_end_date IS NULL)",
            name="ck_farm_crop_cycles_lifecycle_dates",
        ),
        sa.CheckConstraint(
            "planned_end_date >= planned_start_date",
            name="ck_farm_crop_cycles_planned_dates",
        ),
        sa.CheckConstraint(
            "status in ('planned', 'active', 'completed', 'cancelled')",
            name="ck_farm_crop_cycles_status",
        ),
        sa.ForeignKeyConstraint(["crop_id"], ["farm_crops.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["plot_id"], ["farm_plots.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["variety_id"], ["farm_crop_varieties.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farm_crop_cycles_crop_id"), "farm_crop_cycles", ["crop_id"])
    op.create_index(op.f("ix_farm_crop_cycles_plot_id"), "farm_crop_cycles", ["plot_id"])
    op.create_index(
        op.f("ix_farm_crop_cycles_variety_id"), "farm_crop_cycles", ["variety_id"]
    )
    op.create_index(
        "ix_farm_crop_cycles_plot_status_dates",
        "farm_crop_cycles",
        ["plot_id", "status", "planned_start_date", "planned_end_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_farm_crop_cycles_plot_status_dates", table_name="farm_crop_cycles")
    op.drop_index(op.f("ix_farm_crop_cycles_variety_id"), table_name="farm_crop_cycles")
    op.drop_index(op.f("ix_farm_crop_cycles_plot_id"), table_name="farm_crop_cycles")
    op.drop_index(op.f("ix_farm_crop_cycles_crop_id"), table_name="farm_crop_cycles")
    op.drop_table("farm_crop_cycles")
