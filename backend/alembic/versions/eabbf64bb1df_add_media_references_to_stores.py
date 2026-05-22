"""add media references to stores

Revision ID: eabbf64bb1df
Revises: 819387792796
Create Date: 2026-05-21 08:59:14.924897

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'eabbf64bb1df'
down_revision: str | Sequence[str] | None = '819387792796'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "stores",
        sa.Column("logo_media_file_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "stores",
        sa.Column("banner_media_file_id", sa.BigInteger(), nullable=True),
    )

    op.create_foreign_key(
        "fk_stores_logo_media_file_id_media_files",
        "stores",
        "media_files",
        ["logo_media_file_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_stores_banner_media_file_id_media_files",
        "stores",
        "media_files",
        ["banner_media_file_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_stores_logo_media_file_id",
        "stores",
        ["logo_media_file_id"],
    )
    op.create_index(
        "ix_stores_banner_media_file_id",
        "stores",
        ["banner_media_file_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_stores_banner_media_file_id", table_name="stores")
    op.drop_index("ix_stores_logo_media_file_id", table_name="stores")

    op.drop_constraint(
        "fk_stores_banner_media_file_id_media_files",
        "stores",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_stores_logo_media_file_id_media_files",
        "stores",
        type_="foreignkey",
    )

    op.drop_column("stores", "banner_media_file_id")
    op.drop_column("stores", "logo_media_file_id")
