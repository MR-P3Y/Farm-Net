"""add farm reference foundation

Revision ID: c3e7a9f41b02
Revises: b8d4f2c71e04
Create Date: 2026-07-25 22:10:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "c3e7a9f41b02"
down_revision: str | Sequence[str] | None = "b8d4f2c71e04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "farm_measurement_units",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("symbol", sa.String(length=30), nullable=False),
        sa.Column("dimension", sa.String(length=30), nullable=False),
        sa.Column("factor_to_base", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("is_base", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "factor_to_base > 0",
            name="ck_farm_measurement_units_factor_positive",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(
        op.f("ix_farm_measurement_units_dimension"),
        "farm_measurement_units",
        ["dimension"],
    )
    op.create_index(
        "ix_farm_measurement_units_dimension_active_sort",
        "farm_measurement_units",
        ["dimension", "is_active", "sort_order"],
    )

    op.create_table(
        "farm_crop_categories",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(
        "ix_farm_crop_categories_active_sort",
        "farm_crop_categories",
        ["is_active", "sort_order"],
    )

    op.create_table(
        "farm_crops",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("scientific_name", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_cycle_type", sa.String(length=30), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "default_cycle_type in ('annual', 'perennial')",
            name="ck_farm_crops_cycle_type",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["farm_crop_categories.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint(
            "scientific_name",
            name="uq_farm_crops_scientific_name",
        ),
    )
    op.create_index(
        op.f("ix_farm_crops_category_id"),
        "farm_crops",
        ["category_id"],
    )
    op.create_index(op.f("ix_farm_crops_title"), "farm_crops", ["title"])
    op.create_index(
        "ix_farm_crops_category_active_sort",
        "farm_crops",
        ["category_id", "is_active", "sort_order"],
    )

    op.create_table(
        "farm_crop_varieties",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("crop_id", sa.BigInteger(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("scientific_name", sa.String(length=220), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["crop_id"],
            ["farm_crops.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "crop_id",
            "code",
            name="uq_farm_crop_varieties_crop_code",
        ),
    )
    op.create_index(
        op.f("ix_farm_crop_varieties_crop_id"),
        "farm_crop_varieties",
        ["crop_id"],
    )
    op.create_index(
        "ix_farm_crop_varieties_crop_active_sort",
        "farm_crop_varieties",
        ["crop_id", "is_active", "sort_order"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_farm_crop_varieties_crop_active_sort",
        table_name="farm_crop_varieties",
    )
    op.drop_index(
        op.f("ix_farm_crop_varieties_crop_id"),
        table_name="farm_crop_varieties",
    )
    op.drop_table("farm_crop_varieties")

    op.drop_index("ix_farm_crops_category_active_sort", table_name="farm_crops")
    op.drop_index(op.f("ix_farm_crops_title"), table_name="farm_crops")
    op.drop_index(op.f("ix_farm_crops_category_id"), table_name="farm_crops")
    op.drop_table("farm_crops")

    op.drop_index(
        "ix_farm_crop_categories_active_sort",
        table_name="farm_crop_categories",
    )
    op.drop_table("farm_crop_categories")

    op.drop_index(
        "ix_farm_measurement_units_dimension_active_sort",
        table_name="farm_measurement_units",
    )
    op.drop_index(
        op.f("ix_farm_measurement_units_dimension"),
        table_name="farm_measurement_units",
    )
    op.drop_table("farm_measurement_units")
