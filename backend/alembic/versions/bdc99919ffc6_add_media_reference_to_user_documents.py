"""add media reference to user documents

Revision ID: bdc99919ffc6
Revises: eabbf64bb1df
Create Date: 2026-05-21 09:10:31.926616

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'bdc99919ffc6'
down_revision: str | Sequence[str] | None = 'eabbf64bb1df'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user_documents",
        sa.Column("media_file_id", sa.BigInteger(), nullable=True),
    )

    op.create_foreign_key(
        "fk_user_documents_media_file_id_media_files",
        "user_documents",
        "media_files",
        ["media_file_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_user_documents_media_file_id",
        "user_documents",
        ["media_file_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_documents_media_file_id",
        table_name="user_documents",
    )
    op.drop_constraint(
        "fk_user_documents_media_file_id_media_files",
        "user_documents",
        type_="foreignkey",
    )
    op.drop_column("user_documents", "media_file_id")
