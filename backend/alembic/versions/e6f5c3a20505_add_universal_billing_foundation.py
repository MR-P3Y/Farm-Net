"""add universal invoice and commission foundation

Revision ID: e6f5c3a20505
Revises: d9a4b2f20404
Create Date: 2026-07-20 00:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "e6f5c3a20505"
down_revision: str | Sequence[str] | None = "d9a4b2f20404"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "finance_commission_policies",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("percent >= 0 AND percent <= 100", name="ck_commission_policy_percent"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_commission_policy_source_default", "finance_commission_policies", ["source_type", "status", "is_default"])
    for column in ("is_default", "source_type", "status"):
        op.create_index(op.f(f"ix_finance_commission_policies_{column}"), "finance_commission_policies", [column])

    op.create_table(
        "finance_billing_invoices",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("invoice_number", sa.String(70), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("legacy_invoice_id", sa.BigInteger(), nullable=True),
        sa.Column("payer_user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider_user_id", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("subtotal_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("surcharge_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("platform_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("provider_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("refunded_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("currency = 'TOMAN'", name="ck_billing_invoice_currency_toman"),
        sa.CheckConstraint("subtotal_amount >= 0", name="ck_billing_invoice_subtotal"),
        sa.CheckConstraint("discount_amount >= 0", name="ck_billing_invoice_discount"),
        sa.CheckConstraint("surcharge_amount >= 0", name="ck_billing_invoice_surcharge"),
        sa.CheckConstraint("total_amount > 0", name="ck_billing_invoice_total"),
        sa.CheckConstraint("platform_amount >= 0", name="ck_billing_invoice_platform"),
        sa.CheckConstraint("provider_amount >= 0", name="ck_billing_invoice_provider"),
        sa.CheckConstraint("platform_amount + provider_amount = total_amount", name="ck_billing_invoice_split_total"),
        sa.ForeignKeyConstraint(["legacy_invoice_id"], ["finance_invoices.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["payer_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["provider_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_number"),
        sa.UniqueConstraint("source_type", "source_id", name="uq_billing_invoice_source"),
    )
    op.create_index("ix_billing_invoice_payer_status", "finance_billing_invoices", ["payer_user_id", "status"])
    op.create_index("ix_billing_invoice_provider_status", "finance_billing_invoices", ["provider_user_id", "status"])
    for column in ("legacy_invoice_id", "payer_user_id", "provider_user_id", "source_type", "status"):
        op.create_index(op.f(f"ix_finance_billing_invoices_{column}"), "finance_billing_invoices", [column], unique=column == "legacy_invoice_id")

    op.create_table(
        "finance_billing_invoice_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.BigInteger(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("source_item_type", sa.String(50), nullable=False),
        sa.Column("source_item_id", sa.BigInteger(), nullable=True),
        sa.Column("title_snapshot", sa.String(255), nullable=False),
        sa.Column("description_snapshot", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Numeric(18, 3), nullable=False),
        sa.Column("unit_snapshot", sa.String(40), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(18, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("sequence > 0", name="ck_billing_item_sequence"),
        sa.CheckConstraint("quantity > 0", name="ck_billing_item_quantity"),
        sa.CheckConstraint("unit_price >= 0", name="ck_billing_item_unit_price"),
        sa.CheckConstraint("line_total >= 0", name="ck_billing_item_line_total"),
        sa.ForeignKeyConstraint(["invoice_id"], ["finance_billing_invoices.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_id", "sequence", name="uq_billing_invoice_item_sequence"),
    )
    op.create_index(op.f("ix_finance_billing_invoice_items_invoice_id"), "finance_billing_invoice_items", ["invoice_id"])

    op.create_table(
        "finance_billing_commission_snapshots",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.BigInteger(), nullable=False),
        sa.Column("policy_id", sa.BigInteger(), nullable=True),
        sa.Column("legacy_snapshot_id", sa.BigInteger(), nullable=True),
        sa.Column("calculation_type", sa.String(30), nullable=False),
        sa.Column("percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("base_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("platform_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("provider_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("percent >= 0 AND percent <= 100", name="ck_billing_commission_percent"),
        sa.CheckConstraint("base_amount >= 0", name="ck_billing_commission_base"),
        sa.CheckConstraint("platform_amount >= 0", name="ck_billing_commission_platform"),
        sa.CheckConstraint("provider_amount >= 0", name="ck_billing_commission_provider"),
        sa.ForeignKeyConstraint(["invoice_id"], ["finance_billing_invoices.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["legacy_snapshot_id"], ["commission_snapshots.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["policy_id"], ["finance_commission_policies.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_id"),
        sa.UniqueConstraint("legacy_snapshot_id"),
    )
    op.create_index(op.f("ix_finance_billing_commission_snapshots_policy_id"), "finance_billing_commission_snapshots", ["policy_id"])


def downgrade() -> None:
    op.drop_table("finance_billing_commission_snapshots")
    op.drop_table("finance_billing_invoice_items")
    op.drop_table("finance_billing_invoices")
    op.drop_table("finance_commission_policies")
