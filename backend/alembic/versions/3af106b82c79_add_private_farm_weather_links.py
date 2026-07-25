"""add private farm weather links

Revision ID: 3af106b82c79
Revises: 29edf5a07168
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "3af106b82c79"
down_revision: str | Sequence[str] | None = "29edf5a07168"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "weather_locations",
        sa.Column("owner_user_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "weather_locations",
        sa.Column("visibility", sa.String(20), nullable=False, server_default="public"),
    )
    op.create_foreign_key(
        "fk_weather_locations_owner_user_id",
        "weather_locations", "auth_users", ["owner_user_id"], ["id"],
        ondelete="RESTRICT",
    )
    op.create_check_constraint(
        "ck_weather_locations_visibility_owner",
        "weather_locations",
        "(visibility = 'public' AND owner_user_id IS NULL) OR "
        "(visibility = 'private' AND owner_user_id IS NOT NULL)",
    )
    op.create_index(
        op.f("ix_weather_locations_owner_user_id"),
        "weather_locations", ["owner_user_id"],
    )
    op.create_index(
        op.f("ix_weather_locations_visibility"),
        "weather_locations", ["visibility"],
    )
    op.alter_column("weather_locations", "visibility", server_default=None)

    op.create_table(
        "farm_plot_weather_links",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("plot_id", sa.BigInteger(), nullable=False),
        sa.Column("weather_location_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["plot_id"], ["farm_plots.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["weather_location_id"], ["weather_locations.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_farm_plot_weather_links_plot_id"),
        "farm_plot_weather_links", ["plot_id"], unique=True,
    )
    op.create_index(
        op.f("ix_farm_plot_weather_links_weather_location_id"),
        "farm_plot_weather_links", ["weather_location_id"], unique=True,
    )


def downgrade() -> None:
    op.drop_table("farm_plot_weather_links")
    op.drop_constraint(
        "ck_weather_locations_visibility_owner",
        "weather_locations", type_="check",
    )
    op.drop_constraint(
        "fk_weather_locations_owner_user_id",
        "weather_locations", type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_weather_locations_visibility"), table_name="weather_locations"
    )
    op.drop_index(
        op.f("ix_weather_locations_owner_user_id"), table_name="weather_locations"
    )
    op.drop_column("weather_locations", "visibility")
    op.drop_column("weather_locations", "owner_user_id")
