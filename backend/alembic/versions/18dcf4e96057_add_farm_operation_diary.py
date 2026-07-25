"""add farm operation diary

Revision ID: 18dcf4e96057
Revises: 07cbe3d85f46
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "18dcf4e96057"
down_revision: str | Sequence[str] | None = "07cbe3d85f46"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "farm_operations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("cycle_id", sa.BigInteger(), nullable=False),
        sa.Column("operation_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "operation_type in ('land_preparation','planting','irrigation','fertilizing',"
            "'spraying','weeding','pruning','monitoring','other')",
            name="ck_farm_operations_type",
        ),
        sa.ForeignKeyConstraint(["cycle_id"], ["farm_crop_cycles.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farm_operations_cycle_id"), "farm_operations", ["cycle_id"])
    op.create_index("ix_farm_operations_cycle_occurred", "farm_operations", ["cycle_id", "occurred_on"])

    op.create_table(
        "farm_operation_inputs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("operation_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 3), nullable=False),
        sa.Column("measurement_unit_id", sa.BigInteger(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_farm_operation_inputs_quantity_positive"),
        sa.ForeignKeyConstraint(["measurement_unit_id"], ["farm_measurement_units.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["operation_id"], ["farm_operations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farm_operation_inputs_operation_id"), "farm_operation_inputs", ["operation_id"])
    op.create_index(op.f("ix_farm_operation_inputs_measurement_unit_id"), "farm_operation_inputs", ["measurement_unit_id"])

    op.create_table(
        "farm_harvest_observations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("cycle_id", sa.BigInteger(), nullable=False),
        sa.Column("harvested_on", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 3), nullable=False),
        sa.Column("measurement_unit_id", sa.BigInteger(), nullable=False),
        sa.Column("quality_grade", sa.String(80), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_farm_harvest_quantity_positive"),
        sa.ForeignKeyConstraint(["cycle_id"], ["farm_crop_cycles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["measurement_unit_id"], ["farm_measurement_units.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farm_harvest_observations_cycle_id"), "farm_harvest_observations", ["cycle_id"])
    op.create_index(op.f("ix_farm_harvest_observations_measurement_unit_id"), "farm_harvest_observations", ["measurement_unit_id"])
    op.create_index("ix_farm_harvest_cycle_date", "farm_harvest_observations", ["cycle_id", "harvested_on"])

    op.create_table(
        "farm_record_media",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("cycle_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_id", sa.BigInteger(), nullable=True),
        sa.Column("harvest_id", sa.BigInteger(), nullable=True),
        sa.Column("media_file_id", sa.BigInteger(), nullable=False),
        sa.Column("caption", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "(cycle_id IS NOT NULL) + (operation_id IS NOT NULL) + (harvest_id IS NOT NULL) = 1",
            name="ck_farm_record_media_exact_subject",
        ),
        sa.ForeignKeyConstraint(["cycle_id"], ["farm_crop_cycles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["operation_id"], ["farm_operations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["harvest_id"], ["farm_harvest_observations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["media_file_id"], ["media_files.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cycle_id", "media_file_id", name="uq_farm_record_media_cycle_file"),
        sa.UniqueConstraint("operation_id", "media_file_id", name="uq_farm_record_media_operation_file"),
        sa.UniqueConstraint("harvest_id", "media_file_id", name="uq_farm_record_media_harvest_file"),
    )
    for column in ("cycle_id", "operation_id", "harvest_id", "media_file_id"):
        op.create_index(op.f(f"ix_farm_record_media_{column}"), "farm_record_media", [column])


def downgrade() -> None:
    op.drop_table("farm_record_media")
    op.drop_table("farm_harvest_observations")
    op.drop_table("farm_operation_inputs")
    op.drop_table("farm_operations")
