"""add media file reference to product images

Revision ID: 819387792796
Revises: 3744815d3d2e
Create Date: 2026-05-21 08:45:03.876255

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '819387792796'
down_revision: str | Sequence[str] | None = '3744815d3d2e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "product_images",
        sa.Column("media_file_id", sa.BigInteger(), nullable=True),
    )

    op.create_foreign_key(
        "fk_product_images_media_file_id_media_files",
        "product_images",
        "media_files",
        ["media_file_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_product_images_media_file_id",
        "product_images",
        ["media_file_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_product_images_media_file_id", table_name="product_images")
    op.drop_constraint(
        "fk_product_images_media_file_id_media_files",
        "product_images",
        type_="foreignkey",
    )
    op.drop_column("product_images", "media_file_id")
