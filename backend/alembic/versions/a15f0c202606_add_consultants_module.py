"""add consultants module

Revision ID: a15f0c202606
Revises: 59bb20547fd2
Create Date: 2026-06-22 00:30:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "a15f0c202606"
down_revision: str | Sequence[str] | None = "59bb20547fd2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "consult_specialties",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_consult_specialties_code"), "consult_specialties", ["code"], unique=True)
    op.create_index(op.f("ix_consult_specialties_is_active"), "consult_specialties", ["is_active"], unique=False)
    op.create_index(op.f("ix_consult_specialties_title"), "consult_specialties", ["title"], unique=False)
    op.create_index("ix_consult_specialties_active_sort", "consult_specialties", ["is_active", "sort_order"], unique=False)

    op.create_table(
        "consult_profiles",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("display_name", sa.String(length=150), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("experience_years", sa.BigInteger(), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("province_id", sa.BigInteger(), nullable=True),
        sa.Column("city_id", sa.BigInteger(), nullable=True),
        sa.Column("province_name", sa.String(length=120), nullable=True),
        sa.Column("city_name", sa.String(length=120), nullable=True),
        sa.Column("avatar_file_id", sa.String(length=255), nullable=True),
        sa.Column("avatar_media_file_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("rating_average", sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column("reviews_count", sa.BigInteger(), nullable=False),
        sa.Column("requests_count", sa.BigInteger(), nullable=False),
        sa.Column("completed_requests_count", sa.BigInteger(), nullable=False),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("approved_by", sa.BigInteger(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_by", sa.BigInteger(), nullable=True),
        sa.Column("suspended_at", sa.DateTime(), nullable=True),
        sa.Column("suspended_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["approved_by"], ["auth_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["avatar_media_file_id"], ["media_files.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["rejected_by"], ["auth_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["suspended_by"], ["auth_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_consult_profiles_approved_by"), "consult_profiles", ["approved_by"], unique=False)
    op.create_index(op.f("ix_consult_profiles_avatar_media_file_id"), "consult_profiles", ["avatar_media_file_id"], unique=False)
    op.create_index(op.f("ix_consult_profiles_city_id"), "consult_profiles", ["city_id"], unique=False)
    op.create_index(op.f("ix_consult_profiles_is_featured"), "consult_profiles", ["is_featured"], unique=False)
    op.create_index(op.f("ix_consult_profiles_province_id"), "consult_profiles", ["province_id"], unique=False)
    op.create_index(op.f("ix_consult_profiles_rejected_by"), "consult_profiles", ["rejected_by"], unique=False)
    op.create_index(op.f("ix_consult_profiles_status"), "consult_profiles", ["status"], unique=False)
    op.create_index(op.f("ix_consult_profiles_suspended_by"), "consult_profiles", ["suspended_by"], unique=False)
    op.create_index(op.f("ix_consult_profiles_user_id"), "consult_profiles", ["user_id"], unique=True)
    op.create_index("ix_consult_profiles_geo", "consult_profiles", ["province_id", "city_id"], unique=False)
    op.create_index("ix_consult_profiles_rating", "consult_profiles", ["rating_average", "reviews_count"], unique=False)
    op.create_index("ix_consult_profiles_status_featured", "consult_profiles", ["status", "is_featured"], unique=False)

    op.create_table(
        "consult_profile_specialties",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("profile_id", sa.BigInteger(), nullable=False),
        sa.Column("specialty_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["consult_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["specialty_id"], ["consult_specialties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "profile_id",
            "specialty_id",
            name="uq_consult_profile_specialties_profile_specialty",
        ),
    )
    op.create_index(op.f("ix_consult_profile_specialties_profile_id"), "consult_profile_specialties", ["profile_id"], unique=False)
    op.create_index(op.f("ix_consult_profile_specialties_specialty_id"), "consult_profile_specialties", ["specialty_id"], unique=False)

    op.create_table(
        "consult_requests",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("requester_user_id", sa.BigInteger(), nullable=False),
        sa.Column("consultant_profile_id", sa.BigInteger(), nullable=True),
        sa.Column("specialty_id", sa.BigInteger(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("contact_method", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("budget_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("consultant_note", sa.Text(), nullable=True),
        sa.Column("cancel_reason", sa.Text(), nullable=True),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["consultant_profile_id"], ["consult_profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["requester_user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["specialty_id"], ["consult_specialties.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_consult_requests_consultant_profile_id"), "consult_requests", ["consultant_profile_id"], unique=False)
    op.create_index(op.f("ix_consult_requests_requester_user_id"), "consult_requests", ["requester_user_id"], unique=False)
    op.create_index(op.f("ix_consult_requests_specialty_id"), "consult_requests", ["specialty_id"], unique=False)
    op.create_index(op.f("ix_consult_requests_status"), "consult_requests", ["status"], unique=False)
    op.create_index("ix_consult_requests_consultant_status", "consult_requests", ["consultant_profile_id", "status"], unique=False)
    op.create_index("ix_consult_requests_created_status", "consult_requests", ["created_at", "status"], unique=False)
    op.create_index("ix_consult_requests_requester_status", "consult_requests", ["requester_user_id", "status"], unique=False)
    op.create_index("ix_consult_requests_specialty_status", "consult_requests", ["specialty_id", "status"], unique=False)

    op.create_table(
        "consult_request_status_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.BigInteger(), nullable=False),
        sa.Column("changed_by", sa.BigInteger(), nullable=True),
        sa.Column("from_status", sa.String(length=50), nullable=True),
        sa.Column("to_status", sa.String(length=50), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["changed_by"], ["auth_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["request_id"], ["consult_requests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_consult_request_status_logs_changed_by"), "consult_request_status_logs", ["changed_by"], unique=False)
    op.create_index(op.f("ix_consult_request_status_logs_request_id"), "consult_request_status_logs", ["request_id"], unique=False)
    op.create_index(op.f("ix_consult_request_status_logs_to_status"), "consult_request_status_logs", ["to_status"], unique=False)
    op.create_index("ix_consult_request_logs_request_created", "consult_request_status_logs", ["request_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_consult_request_logs_request_created", table_name="consult_request_status_logs")
    op.drop_index(op.f("ix_consult_request_status_logs_to_status"), table_name="consult_request_status_logs")
    op.drop_index(op.f("ix_consult_request_status_logs_request_id"), table_name="consult_request_status_logs")
    op.drop_index(op.f("ix_consult_request_status_logs_changed_by"), table_name="consult_request_status_logs")
    op.drop_table("consult_request_status_logs")

    op.drop_index("ix_consult_requests_specialty_status", table_name="consult_requests")
    op.drop_index("ix_consult_requests_requester_status", table_name="consult_requests")
    op.drop_index("ix_consult_requests_created_status", table_name="consult_requests")
    op.drop_index("ix_consult_requests_consultant_status", table_name="consult_requests")
    op.drop_index(op.f("ix_consult_requests_status"), table_name="consult_requests")
    op.drop_index(op.f("ix_consult_requests_specialty_id"), table_name="consult_requests")
    op.drop_index(op.f("ix_consult_requests_requester_user_id"), table_name="consult_requests")
    op.drop_index(op.f("ix_consult_requests_consultant_profile_id"), table_name="consult_requests")
    op.drop_table("consult_requests")

    op.drop_index(op.f("ix_consult_profile_specialties_specialty_id"), table_name="consult_profile_specialties")
    op.drop_index(op.f("ix_consult_profile_specialties_profile_id"), table_name="consult_profile_specialties")
    op.drop_table("consult_profile_specialties")

    op.drop_index("ix_consult_profiles_status_featured", table_name="consult_profiles")
    op.drop_index("ix_consult_profiles_rating", table_name="consult_profiles")
    op.drop_index("ix_consult_profiles_geo", table_name="consult_profiles")
    op.drop_index(op.f("ix_consult_profiles_user_id"), table_name="consult_profiles")
    op.drop_index(op.f("ix_consult_profiles_suspended_by"), table_name="consult_profiles")
    op.drop_index(op.f("ix_consult_profiles_status"), table_name="consult_profiles")
    op.drop_index(op.f("ix_consult_profiles_rejected_by"), table_name="consult_profiles")
    op.drop_index(op.f("ix_consult_profiles_province_id"), table_name="consult_profiles")
    op.drop_index(op.f("ix_consult_profiles_is_featured"), table_name="consult_profiles")
    op.drop_index(op.f("ix_consult_profiles_city_id"), table_name="consult_profiles")
    op.drop_index(op.f("ix_consult_profiles_avatar_media_file_id"), table_name="consult_profiles")
    op.drop_index(op.f("ix_consult_profiles_approved_by"), table_name="consult_profiles")
    op.drop_table("consult_profiles")

    op.drop_index("ix_consult_specialties_active_sort", table_name="consult_specialties")
    op.drop_index(op.f("ix_consult_specialties_title"), table_name="consult_specialties")
    op.drop_index(op.f("ix_consult_specialties_is_active"), table_name="consult_specialties")
    op.drop_index(op.f("ix_consult_specialties_code"), table_name="consult_specialties")
    op.drop_table("consult_specialties")
