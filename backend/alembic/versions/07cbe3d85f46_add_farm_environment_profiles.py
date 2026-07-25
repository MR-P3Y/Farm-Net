"""add farm environment profiles

Revision ID: 07cbe3d85f46
Revises: f6bad2c74e35
"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "07cbe3d85f46"
down_revision: str | Sequence[str] | None = "f6bad2c74e35"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "farm_soil_profiles",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("plot_id", sa.BigInteger(), nullable=False),
        sa.Column("texture", sa.String(30), nullable=False),
        sa.Column("depth_cm", sa.Numeric(8, 2), nullable=True),
        sa.Column("drainage", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("texture in ('sandy','loamy','clay','silty','mixed','unknown')", name="ck_farm_soil_profiles_texture"),
        sa.CheckConstraint("depth_cm IS NULL OR depth_cm > 0", name="ck_farm_soil_profiles_depth_positive"),
        sa.ForeignKeyConstraint(["plot_id"], ["farm_plots.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_farm_soil_profiles_plot_id"),
        "farm_soil_profiles",
        ["plot_id"],
        unique=True,
    )
    op.create_table(
        "farm_water_sources",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("farm_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("source_type in ('well','spring','river','canal','reservoir','municipal','other')", name="ck_farm_water_sources_type"),
        sa.CheckConstraint("(status = 'active' AND archived_at IS NULL) OR (status = 'archived' AND archived_at IS NOT NULL)", name="ck_farm_water_sources_archive_state"),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farm_water_sources_farm_id"), "farm_water_sources", ["farm_id"])
    op.create_index("ix_farm_water_sources_farm_status", "farm_water_sources", ["farm_id", "status"])
    op.create_table(
        "farm_irrigation_profiles",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("plot_id", sa.BigInteger(), nullable=False),
        sa.Column("water_source_id", sa.BigInteger(), nullable=True),
        sa.Column("method", sa.String(30), nullable=False),
        sa.Column("efficiency_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("method in ('surface','drip','sprinkler','subsurface','rainfed','other')", name="ck_farm_irrigation_profiles_method"),
        sa.CheckConstraint("efficiency_percent IS NULL OR (efficiency_percent >= 0 AND efficiency_percent <= 100)", name="ck_farm_irrigation_profiles_efficiency"),
        sa.ForeignKeyConstraint(["plot_id"], ["farm_plots.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["water_source_id"], ["farm_water_sources.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_farm_irrigation_profiles_plot_id"),
        "farm_irrigation_profiles",
        ["plot_id"],
        unique=True,
    )
    op.create_index(op.f("ix_farm_irrigation_profiles_water_source_id"), "farm_irrigation_profiles", ["water_source_id"])
    op.create_table(
        "farm_lab_observations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("soil_profile_id", sa.BigInteger(), nullable=True),
        sa.Column("water_source_id", sa.BigInteger(), nullable=True),
        sa.Column("metric_code", sa.String(50), nullable=False),
        sa.Column("value", sa.Numeric(20, 6), nullable=False),
        sa.Column("unit_code", sa.String(30), nullable=False),
        sa.Column("sampled_on", sa.Date(), nullable=False),
        sa.Column("tested_on", sa.Date(), nullable=True),
        sa.Column("laboratory_name", sa.String(200), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("(soil_profile_id IS NOT NULL AND water_source_id IS NULL) OR (soil_profile_id IS NULL AND water_source_id IS NOT NULL)", name="ck_farm_lab_observations_exact_subject"),
        sa.CheckConstraint("value >= 0", name="ck_farm_lab_observations_value_nonnegative"),
        sa.CheckConstraint("tested_on IS NULL OR tested_on >= sampled_on", name="ck_farm_lab_observations_dates"),
        sa.ForeignKeyConstraint(["soil_profile_id"], ["farm_soil_profiles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["water_source_id"], ["farm_water_sources.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farm_lab_observations_soil_profile_id"), "farm_lab_observations", ["soil_profile_id"])
    op.create_index(op.f("ix_farm_lab_observations_water_source_id"), "farm_lab_observations", ["water_source_id"])
    op.create_index("ix_farm_lab_observations_soil_sampled", "farm_lab_observations", ["soil_profile_id", "sampled_on"])
    op.create_index("ix_farm_lab_observations_water_sampled", "farm_lab_observations", ["water_source_id", "sampled_on"])


def downgrade() -> None:
    op.drop_table("farm_lab_observations")
    op.drop_table("farm_irrigation_profiles")
    op.drop_table("farm_water_sources")
    op.drop_table("farm_soil_profiles")
