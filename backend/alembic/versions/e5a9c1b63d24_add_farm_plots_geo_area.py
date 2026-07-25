"""add farm plots geo and area

Revision ID: e5a9c1b63d24
Revises: d4f8b0a52c13
Create Date: 2026-07-26 00:10:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "e5a9c1b63d24"
down_revision: str | Sequence[str] | None = "d4f8b0a52c13"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "farms",
        sa.Column("declared_area_sqm", sa.Numeric(precision=18, scale=2), nullable=True),
    )
    op.create_check_constraint(
        "ck_farms_declared_area_positive",
        "farms",
        "declared_area_sqm IS NULL OR declared_area_sqm > 0",
    )

    op.create_table(
        "farm_plots",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("farm_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("area_sqm", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("province_id", sa.BigInteger(), nullable=True),
        sa.Column("county_id", sa.BigInteger(), nullable=True),
        sa.Column("district_id", sa.BigInteger(), nullable=True),
        sa.Column("rural_district_id", sa.BigInteger(), nullable=True),
        sa.Column("city_id", sa.BigInteger(), nullable=True),
        sa.Column("village_id", sa.BigInteger(), nullable=True),
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("boundary", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("archive_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("area_sqm > 0", name="ck_farm_plots_area_positive"),
        sa.CheckConstraint(
            "(status = 'active' AND archived_at IS NULL AND archive_reason IS NULL) "
            "OR (status = 'archived' AND archived_at IS NOT NULL)",
            name="ck_farm_plots_archive_state",
        ),
        sa.CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="ck_farm_plots_coordinate_pair",
        ),
        sa.CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="ck_farm_plots_latitude",
        ),
        sa.CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="ck_farm_plots_longitude",
        ),
        sa.CheckConstraint(
            "status in ('active', 'archived')",
            name="ck_farm_plots_status",
        ),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["province_id"], ["geo_provinces.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["county_id"], ["geo_counties.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["district_id"], ["geo_districts.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["rural_district_id"],
            ["geo_rural_districts.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(["city_id"], ["geo_cities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["village_id"], ["geo_villages.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farm_plots_farm_id"), "farm_plots", ["farm_id"])
    op.create_index(
        "ix_farm_plots_farm_status_updated",
        "farm_plots",
        ["farm_id", "status", "updated_at"],
    )
    op.create_index(
        "ix_farm_plots_geo",
        "farm_plots",
        [
            "province_id",
            "county_id",
            "district_id",
            "rural_district_id",
            "city_id",
            "village_id",
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_farm_plots_geo", table_name="farm_plots")
    op.drop_index("ix_farm_plots_farm_status_updated", table_name="farm_plots")
    op.drop_index(op.f("ix_farm_plots_farm_id"), table_name="farm_plots")
    op.drop_table("farm_plots")
    op.drop_constraint("ck_farms_declared_area_positive", "farms", type_="check")
    op.drop_column("farms", "declared_area_sqm")
