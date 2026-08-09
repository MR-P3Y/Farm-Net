"""add universal user favorites

Revision ID: n26b2c3d4e5f
Revises: m26a1b2c3d4e
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "n26b2c3d4e5f"
down_revision: str | None = "m26a1b2c3d4e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_favorites",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("subject_type", sa.String(length=40), nullable=False),
        sa.Column("subject_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "subject_id > 0",
            name="ck_user_favorites_subject_id_positive",
        ),
        sa.CheckConstraint(
            "subject_type IN "
            "('product', 'store', 'service_offer', 'rental_equipment', "
            "'consultant', 'social_post')",
            name="ck_user_favorites_subject_type",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth_users.id"],
            name="fk_user_favorites_user_id_auth_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "subject_type",
            "subject_id",
            name="uq_user_favorites_owner_subject",
        ),
    )
    op.create_index(
        "ix_user_favorites_user_id",
        "user_favorites",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_favorites_subject_type",
        "user_favorites",
        ["subject_type"],
        unique=False,
    )
    op.create_index(
        "ix_user_favorites_owner_created",
        "user_favorites",
        ["user_id", "created_at", "id"],
        unique=False,
    )
    op.create_index(
        "ix_user_favorites_subject",
        "user_favorites",
        ["subject_type", "subject_id"],
        unique=False,
    )

    op.execute(
        sa.text(
            """
            INSERT IGNORE INTO user_favorites
                (user_id, subject_type, subject_id, created_at)
            SELECT user_id, 'social_post', post_id, created_at
            FROM social_bookmarks
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_user_favorites_subject", table_name="user_favorites")
    op.drop_index("ix_user_favorites_owner_created", table_name="user_favorites")
    op.drop_index("ix_user_favorites_subject_type", table_name="user_favorites")
    op.drop_index("ix_user_favorites_user_id", table_name="user_favorites")
    op.drop_table("user_favorites")
