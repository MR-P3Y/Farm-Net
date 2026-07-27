"""add Barzegar image evidence binding

Revision ID: j21f7d4b0918
Revises: i21e6c3af807
Create Date: 2026-07-28 02:10:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "j21f7d4b0918"
down_revision: str | Sequence[str] | None = "i21e6c3af807"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_request_media",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.BigInteger(), nullable=False),
        sa.Column("media_file_id", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "mime_type IN ('image/jpeg','image/png','image/webp')",
            name="ck_ai_request_media_mime",
        ),
        sa.CheckConstraint(
            "size_bytes BETWEEN 1 AND 10485760", name="ck_ai_request_media_size"
        ),
        sa.CheckConstraint(
            "width >= 256 AND height >= 256", name="ck_ai_request_media_dimensions"
        ),
        sa.ForeignKeyConstraint(["media_file_id"], ["media_files.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["request_id"], ["ai_requests.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("media_file_id"),
        sa.UniqueConstraint("request_id"),
    )


def downgrade() -> None:
    op.drop_table("ai_request_media")
