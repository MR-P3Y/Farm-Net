"""remove duplicate consultant and service unique indexes

Revision ID: b8d4f2c71e04
Revises: a7c9e1f30d13
Create Date: 2026-07-24 18:00:00.000000

"""

from collections.abc import Sequence

from alembic import op


revision: str = "b8d4f2c71e04"
down_revision: str | Sequence[str] | None = "a7c9e1f30d13"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DUPLICATE_INDEXES = (
    ("consult_specialties", "code", "code"),
    ("consult_profiles", "user_id", "user_id"),
    ("service_categories", "code", "code"),
    ("service_provider_profiles", "user_id", "user_id"),
)


def upgrade() -> None:
    for table_name, index_name, _ in DUPLICATE_INDEXES:
        op.drop_index(index_name, table_name=table_name)


def downgrade() -> None:
    for table_name, index_name, column_name in DUPLICATE_INDEXES:
        op.create_index(
            index_name,
            table_name,
            [column_name],
            unique=True,
        )
