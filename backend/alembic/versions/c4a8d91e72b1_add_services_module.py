"""add services module

Revision ID: c4a8d91e72b1
Revises: a15f0c202606
Create Date: 2026-07-02 00:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "c4a8d91e72b1"
down_revision: str | Sequence[str] | None = "a15f0c202606"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "service_categories",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["service_categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_service_categories_code"), "service_categories", ["code"], unique=True)
    op.create_index(op.f("ix_service_categories_is_active"), "service_categories", ["is_active"], unique=False)
    op.create_index(op.f("ix_service_categories_parent_id"), "service_categories", ["parent_id"], unique=False)
    op.create_index(op.f("ix_service_categories_title"), "service_categories", ["title"], unique=False)
    op.create_index("ix_service_categories_active_sort", "service_categories", ["is_active", "sort_order"], unique=False)
    op.create_index("ix_service_categories_parent_active", "service_categories", ["parent_id", "is_active"], unique=False)

    op.create_table(
        "service_provider_profiles",
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
        sa.Column("village_id", sa.BigInteger(), nullable=True),
        sa.Column("province_name", sa.String(length=120), nullable=True),
        sa.Column("city_name", sa.String(length=120), nullable=True),
        sa.Column("village_name", sa.String(length=120), nullable=True),
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
    op.create_index(op.f("ix_service_provider_profiles_approved_by"), "service_provider_profiles", ["approved_by"], unique=False)
    op.create_index(op.f("ix_service_provider_profiles_avatar_media_file_id"), "service_provider_profiles", ["avatar_media_file_id"], unique=False)
    op.create_index(op.f("ix_service_provider_profiles_city_id"), "service_provider_profiles", ["city_id"], unique=False)
    op.create_index(op.f("ix_service_provider_profiles_is_featured"), "service_provider_profiles", ["is_featured"], unique=False)
    op.create_index(op.f("ix_service_provider_profiles_province_id"), "service_provider_profiles", ["province_id"], unique=False)
    op.create_index(op.f("ix_service_provider_profiles_rejected_by"), "service_provider_profiles", ["rejected_by"], unique=False)
    op.create_index(op.f("ix_service_provider_profiles_status"), "service_provider_profiles", ["status"], unique=False)
    op.create_index(op.f("ix_service_provider_profiles_suspended_by"), "service_provider_profiles", ["suspended_by"], unique=False)
    op.create_index(op.f("ix_service_provider_profiles_user_id"), "service_provider_profiles", ["user_id"], unique=True)
    op.create_index(op.f("ix_service_provider_profiles_village_id"), "service_provider_profiles", ["village_id"], unique=False)
    op.create_index("ix_service_provider_profiles_geo", "service_provider_profiles", ["province_id", "city_id", "village_id"], unique=False)
    op.create_index("ix_service_provider_profiles_rating", "service_provider_profiles", ["rating_average", "reviews_count"], unique=False)
    op.create_index("ix_service_provider_profiles_status_featured", "service_provider_profiles", ["status", "is_featured"], unique=False)

    op.create_table(
        "service_provider_categories",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("provider_profile_id", sa.BigInteger(), nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["service_categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["provider_profile_id"], ["service_provider_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider_profile_id",
            "category_id",
            name="uq_service_provider_categories_provider_category",
        ),
    )
    op.create_index(op.f("ix_service_provider_categories_category_id"), "service_provider_categories", ["category_id"], unique=False)
    op.create_index(op.f("ix_service_provider_categories_provider_profile_id"), "service_provider_categories", ["provider_profile_id"], unique=False)

    op.create_table(
        "service_offers",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("provider_profile_id", sa.BigInteger(), nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=True),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("short_description", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("pricing_type", sa.String(length=40), nullable=False),
        sa.Column("price_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("province_id", sa.BigInteger(), nullable=True),
        sa.Column("city_id", sa.BigInteger(), nullable=True),
        sa.Column("village_id", sa.BigInteger(), nullable=True),
        sa.Column("province_name", sa.String(length=120), nullable=True),
        sa.Column("city_name", sa.String(length=120), nullable=True),
        sa.Column("village_name", sa.String(length=120), nullable=True),
        sa.Column("service_area", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.String(length=40), nullable=True),
        sa.Column("longitude", sa.String(length=40), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("views_count", sa.BigInteger(), nullable=False),
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
        sa.ForeignKeyConstraint(["category_id"], ["service_categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["provider_profile_id"], ["service_provider_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rejected_by"], ["auth_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["suspended_by"], ["auth_users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_profile_id", "slug", name="uq_service_offers_provider_slug"),
    )
    op.create_index(op.f("ix_service_offers_approved_by"), "service_offers", ["approved_by"], unique=False)
    op.create_index(op.f("ix_service_offers_category_id"), "service_offers", ["category_id"], unique=False)
    op.create_index(op.f("ix_service_offers_city_id"), "service_offers", ["city_id"], unique=False)
    op.create_index(op.f("ix_service_offers_is_active"), "service_offers", ["is_active"], unique=False)
    op.create_index(op.f("ix_service_offers_is_featured"), "service_offers", ["is_featured"], unique=False)
    op.create_index(op.f("ix_service_offers_pricing_type"), "service_offers", ["pricing_type"], unique=False)
    op.create_index(op.f("ix_service_offers_provider_profile_id"), "service_offers", ["provider_profile_id"], unique=False)
    op.create_index(op.f("ix_service_offers_province_id"), "service_offers", ["province_id"], unique=False)
    op.create_index(op.f("ix_service_offers_rejected_by"), "service_offers", ["rejected_by"], unique=False)
    op.create_index(op.f("ix_service_offers_slug"), "service_offers", ["slug"], unique=False)
    op.create_index(op.f("ix_service_offers_status"), "service_offers", ["status"], unique=False)
    op.create_index(op.f("ix_service_offers_suspended_by"), "service_offers", ["suspended_by"], unique=False)
    op.create_index(op.f("ix_service_offers_title"), "service_offers", ["title"], unique=False)
    op.create_index(op.f("ix_service_offers_village_id"), "service_offers", ["village_id"], unique=False)
    op.create_index("ix_service_offers_category_status", "service_offers", ["category_id", "status"], unique=False)
    op.create_index("ix_service_offers_geo", "service_offers", ["province_id", "city_id", "village_id"], unique=False)
    op.create_index("ix_service_offers_price", "service_offers", ["price_amount"], unique=False)
    op.create_index("ix_service_offers_provider_status", "service_offers", ["provider_profile_id", "status"], unique=False)
    op.create_index("ix_service_offers_public_lookup", "service_offers", ["status", "deleted_at", "is_active"], unique=False)

    op.create_table(
        "service_offer_media",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offer_id", sa.BigInteger(), nullable=False),
        sa.Column("media_file_id", sa.BigInteger(), nullable=True),
        sa.Column("file_id", sa.String(length=255), nullable=True),
        sa.Column("file_path", sa.String(length=1000), nullable=True),
        sa.Column("alt_text", sa.String(length=255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["media_file_id"], ["media_files.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["offer_id"], ["service_offers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_service_offer_media_is_primary"), "service_offer_media", ["is_primary"], unique=False)
    op.create_index(op.f("ix_service_offer_media_media_file_id"), "service_offer_media", ["media_file_id"], unique=False)
    op.create_index(op.f("ix_service_offer_media_offer_id"), "service_offer_media", ["offer_id"], unique=False)
    op.create_index("ix_service_offer_media_offer_primary", "service_offer_media", ["offer_id", "is_primary"], unique=False)
    op.create_index("ix_service_offer_media_offer_sort", "service_offer_media", ["offer_id", "sort_order"], unique=False)

    op.create_table(
        "service_requests",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("requester_user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider_profile_id", sa.BigInteger(), nullable=True),
        sa.Column("offer_id", sa.BigInteger(), nullable=True),
        sa.Column("category_id", sa.BigInteger(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("contact_method", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("budget_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("province_id", sa.BigInteger(), nullable=True),
        sa.Column("city_id", sa.BigInteger(), nullable=True),
        sa.Column("village_id", sa.BigInteger(), nullable=True),
        sa.Column("province_name", sa.String(length=120), nullable=True),
        sa.Column("city_name", sa.String(length=120), nullable=True),
        sa.Column("village_name", sa.String(length=120), nullable=True),
        sa.Column("address_text", sa.Text(), nullable=True),
        sa.Column("latitude", sa.String(length=40), nullable=True),
        sa.Column("longitude", sa.String(length=40), nullable=True),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("provider_note", sa.Text(), nullable=True),
        sa.Column("cancel_reason", sa.Text(), nullable=True),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["service_categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["offer_id"], ["service_offers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["provider_profile_id"], ["service_provider_profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["requester_user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_service_requests_category_id"), "service_requests", ["category_id"], unique=False)
    op.create_index(op.f("ix_service_requests_city_id"), "service_requests", ["city_id"], unique=False)
    op.create_index(op.f("ix_service_requests_contact_method"), "service_requests", ["contact_method"], unique=False)
    op.create_index(op.f("ix_service_requests_offer_id"), "service_requests", ["offer_id"], unique=False)
    op.create_index(op.f("ix_service_requests_provider_profile_id"), "service_requests", ["provider_profile_id"], unique=False)
    op.create_index(op.f("ix_service_requests_province_id"), "service_requests", ["province_id"], unique=False)
    op.create_index(op.f("ix_service_requests_requester_user_id"), "service_requests", ["requester_user_id"], unique=False)
    op.create_index(op.f("ix_service_requests_status"), "service_requests", ["status"], unique=False)
    op.create_index(op.f("ix_service_requests_village_id"), "service_requests", ["village_id"], unique=False)
    op.create_index("ix_service_requests_category_status", "service_requests", ["category_id", "status"], unique=False)
    op.create_index("ix_service_requests_created_status", "service_requests", ["created_at", "status"], unique=False)
    op.create_index("ix_service_requests_offer_status", "service_requests", ["offer_id", "status"], unique=False)
    op.create_index("ix_service_requests_provider_status", "service_requests", ["provider_profile_id", "status"], unique=False)
    op.create_index("ix_service_requests_requester_status", "service_requests", ["requester_user_id", "status"], unique=False)

    op.create_table(
        "service_request_status_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.BigInteger(), nullable=False),
        sa.Column("changed_by", sa.BigInteger(), nullable=True),
        sa.Column("from_status", sa.String(length=50), nullable=True),
        sa.Column("to_status", sa.String(length=50), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["changed_by"], ["auth_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["request_id"], ["service_requests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_service_request_status_logs_changed_by"), "service_request_status_logs", ["changed_by"], unique=False)
    op.create_index(op.f("ix_service_request_status_logs_request_id"), "service_request_status_logs", ["request_id"], unique=False)
    op.create_index(op.f("ix_service_request_status_logs_to_status"), "service_request_status_logs", ["to_status"], unique=False)
    op.create_index("ix_service_request_logs_request_created", "service_request_status_logs", ["request_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_service_request_logs_request_created", table_name="service_request_status_logs")
    op.drop_index(op.f("ix_service_request_status_logs_to_status"), table_name="service_request_status_logs")
    op.drop_index(op.f("ix_service_request_status_logs_request_id"), table_name="service_request_status_logs")
    op.drop_index(op.f("ix_service_request_status_logs_changed_by"), table_name="service_request_status_logs")
    op.drop_table("service_request_status_logs")

    op.drop_index("ix_service_requests_requester_status", table_name="service_requests")
    op.drop_index("ix_service_requests_provider_status", table_name="service_requests")
    op.drop_index("ix_service_requests_offer_status", table_name="service_requests")
    op.drop_index("ix_service_requests_created_status", table_name="service_requests")
    op.drop_index("ix_service_requests_category_status", table_name="service_requests")
    op.drop_index(op.f("ix_service_requests_village_id"), table_name="service_requests")
    op.drop_index(op.f("ix_service_requests_status"), table_name="service_requests")
    op.drop_index(op.f("ix_service_requests_requester_user_id"), table_name="service_requests")
    op.drop_index(op.f("ix_service_requests_province_id"), table_name="service_requests")
    op.drop_index(op.f("ix_service_requests_provider_profile_id"), table_name="service_requests")
    op.drop_index(op.f("ix_service_requests_offer_id"), table_name="service_requests")
    op.drop_index(op.f("ix_service_requests_contact_method"), table_name="service_requests")
    op.drop_index(op.f("ix_service_requests_city_id"), table_name="service_requests")
    op.drop_index(op.f("ix_service_requests_category_id"), table_name="service_requests")
    op.drop_table("service_requests")

    op.drop_index("ix_service_offer_media_offer_sort", table_name="service_offer_media")
    op.drop_index("ix_service_offer_media_offer_primary", table_name="service_offer_media")
    op.drop_index(op.f("ix_service_offer_media_offer_id"), table_name="service_offer_media")
    op.drop_index(op.f("ix_service_offer_media_media_file_id"), table_name="service_offer_media")
    op.drop_index(op.f("ix_service_offer_media_is_primary"), table_name="service_offer_media")
    op.drop_table("service_offer_media")

    op.drop_index("ix_service_offers_public_lookup", table_name="service_offers")
    op.drop_index("ix_service_offers_provider_status", table_name="service_offers")
    op.drop_index("ix_service_offers_price", table_name="service_offers")
    op.drop_index("ix_service_offers_geo", table_name="service_offers")
    op.drop_index("ix_service_offers_category_status", table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_village_id"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_title"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_suspended_by"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_status"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_slug"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_rejected_by"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_province_id"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_provider_profile_id"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_pricing_type"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_is_featured"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_is_active"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_city_id"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_category_id"), table_name="service_offers")
    op.drop_index(op.f("ix_service_offers_approved_by"), table_name="service_offers")
    op.drop_table("service_offers")

    op.drop_index(op.f("ix_service_provider_categories_provider_profile_id"), table_name="service_provider_categories")
    op.drop_index(op.f("ix_service_provider_categories_category_id"), table_name="service_provider_categories")
    op.drop_table("service_provider_categories")

    op.drop_index("ix_service_provider_profiles_status_featured", table_name="service_provider_profiles")
    op.drop_index("ix_service_provider_profiles_rating", table_name="service_provider_profiles")
    op.drop_index("ix_service_provider_profiles_geo", table_name="service_provider_profiles")
    op.drop_index(op.f("ix_service_provider_profiles_village_id"), table_name="service_provider_profiles")
    op.drop_index(op.f("ix_service_provider_profiles_user_id"), table_name="service_provider_profiles")
    op.drop_index(op.f("ix_service_provider_profiles_suspended_by"), table_name="service_provider_profiles")
    op.drop_index(op.f("ix_service_provider_profiles_status"), table_name="service_provider_profiles")
    op.drop_index(op.f("ix_service_provider_profiles_rejected_by"), table_name="service_provider_profiles")
    op.drop_index(op.f("ix_service_provider_profiles_province_id"), table_name="service_provider_profiles")
    op.drop_index(op.f("ix_service_provider_profiles_is_featured"), table_name="service_provider_profiles")
    op.drop_index(op.f("ix_service_provider_profiles_city_id"), table_name="service_provider_profiles")
    op.drop_index(op.f("ix_service_provider_profiles_avatar_media_file_id"), table_name="service_provider_profiles")
    op.drop_index(op.f("ix_service_provider_profiles_approved_by"), table_name="service_provider_profiles")
    op.drop_table("service_provider_profiles")

    op.drop_index("ix_service_categories_parent_active", table_name="service_categories")
    op.drop_index("ix_service_categories_active_sort", table_name="service_categories")
    op.drop_index(op.f("ix_service_categories_title"), table_name="service_categories")
    op.drop_index(op.f("ix_service_categories_parent_id"), table_name="service_categories")
    op.drop_index(op.f("ix_service_categories_is_active"), table_name="service_categories")
    op.drop_index(op.f("ix_service_categories_code"), table_name="service_categories")
    op.drop_table("service_categories")
