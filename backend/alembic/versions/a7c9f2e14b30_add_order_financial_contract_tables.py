"""add order financial contract tables

Revision ID: a7c9f2e14b30
Revises: d62e2f6b7c11
Create Date: 2026-07-17
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "a7c9f2e14b30"
down_revision: str | Sequence[str] | None = "d62e2f6b7c11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "finance_invoices",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("invoice_number", sa.String(50), nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("buyer_user_id", sa.BigInteger(), nullable=False),
        sa.Column("store_id", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("subtotal_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("shipping_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("platform_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("provider_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("refunded_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("subtotal_amount >= 0", name="ck_finance_invoices_subtotal_nonnegative"),
        sa.CheckConstraint("discount_amount >= 0", name="ck_finance_invoices_discount_nonnegative"),
        sa.CheckConstraint("shipping_amount >= 0", name="ck_finance_invoices_shipping_nonnegative"),
        sa.CheckConstraint("total_amount >= 0", name="ck_finance_invoices_total_nonnegative"),
        sa.CheckConstraint("platform_amount >= 0", name="ck_finance_invoices_platform_nonnegative"),
        sa.CheckConstraint("provider_amount >= 0", name="ck_finance_invoices_provider_nonnegative"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["buyer_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_number"),
        sa.UniqueConstraint("order_id"),
    )
    op.create_index("ix_finance_invoices_buyer_user_id", "finance_invoices", ["buyer_user_id"])
    op.create_index("ix_finance_invoices_store_id", "finance_invoices", ["store_id"])
    op.create_index("ix_finance_invoices_status", "finance_invoices", ["status"])
    op.create_index(
        "ix_finance_invoices_buyer_status", "finance_invoices", ["buyer_user_id", "status"]
    )
    op.create_index("ix_finance_invoices_store_status", "finance_invoices", ["store_id", "status"])

    op.create_table(
        "finance_invoice_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.BigInteger(), nullable=False),
        sa.Column("order_item_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("title_snapshot", sa.String(220), nullable=False),
        sa.Column("sku_snapshot", sa.String(120), nullable=True),
        sa.Column("unit_snapshot", sa.String(30), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_finance_invoice_items_quantity_positive"),
        sa.CheckConstraint("unit_price >= 0", name="ck_finance_invoice_items_price_nonnegative"),
        sa.CheckConstraint("line_total >= 0", name="ck_finance_invoice_items_total_nonnegative"),
        sa.ForeignKeyConstraint(["invoice_id"], ["finance_invoices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_item_id"], ["order_items.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["product_id"], ["store_products.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_item_id"),
    )
    op.create_index("ix_finance_invoice_items_invoice_id", "finance_invoice_items", ["invoice_id"])
    op.create_index("ix_finance_invoice_items_product_id", "finance_invoice_items", ["product_id"])

    op.create_table(
        "commission_snapshots",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("invoice_id", sa.BigInteger(), nullable=False),
        sa.Column("commission_setting_id", sa.BigInteger(), nullable=True),
        sa.Column("calculation_type", sa.String(30), nullable=False),
        sa.Column("percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("base_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("platform_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("provider_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "percent >= 0 AND percent <= 100", name="ck_commission_snapshots_percent"
        ),
        sa.CheckConstraint("base_amount >= 0", name="ck_commission_snapshots_base_nonnegative"),
        sa.CheckConstraint(
            "platform_amount >= 0", name="ck_commission_snapshots_platform_nonnegative"
        ),
        sa.CheckConstraint(
            "provider_amount >= 0", name="ck_commission_snapshots_provider_nonnegative"
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["invoice_id"], ["finance_invoices.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["commission_setting_id"], ["commission_settings.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id"),
        sa.UniqueConstraint("invoice_id"),
    )

    op.create_table(
        "payment_attempts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.BigInteger(), nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("legacy_payment_id", sa.BigInteger(), nullable=True),
        sa.Column("provider", sa.String(80), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("idempotency_key", sa.String(160), nullable=False),
        sa.Column("provider_payment_id", sa.String(255), nullable=True),
        sa.Column("provider_reference", sa.String(255), nullable=True),
        sa.Column("redirect_url", sa.Text(), nullable=True),
        sa.Column("callback_payload", sa.Text(), nullable=True),
        sa.Column("verify_payload", sa.Text(), nullable=True),
        sa.Column("failure_code", sa.String(100), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("verified_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_payment_attempts_amount_positive"),
        sa.ForeignKeyConstraint(["invoice_id"], ["finance_invoices.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["legacy_payment_id"], ["payments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
        sa.UniqueConstraint("provider_payment_id"),
        sa.UniqueConstraint("provider_reference"),
    )
    op.create_index("ix_payment_attempts_invoice_id", "payment_attempts", ["invoice_id"])
    op.create_index("ix_payment_attempts_order_id", "payment_attempts", ["order_id"])
    op.create_index("ix_payment_attempts_user_id", "payment_attempts", ["user_id"])
    op.create_index("ix_payment_attempts_provider", "payment_attempts", ["provider"])
    op.create_index("ix_payment_attempts_status", "payment_attempts", ["status"])
    op.create_index(
        "ix_payment_attempts_invoice_status", "payment_attempts", ["invoice_id", "status"]
    )

    op.create_table(
        "finance_transactions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.BigInteger(), nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("payment_attempt_id", sa.BigInteger(), nullable=True),
        sa.Column("transaction_type", sa.String(40), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("provider", sa.String(80), nullable=True),
        sa.Column("provider_reference", sa.String(255), nullable=True),
        sa.Column("idempotency_key", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_finance_transactions_amount_positive"),
        sa.ForeignKeyConstraint(["invoice_id"], ["finance_invoices.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["payment_attempt_id"], ["payment_attempts.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_reference"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("ix_finance_transactions_invoice_id", "finance_transactions", ["invoice_id"])
    op.create_index("ix_finance_transactions_order_id", "finance_transactions", ["order_id"])
    op.create_index(
        "ix_finance_transactions_payment_attempt_id", "finance_transactions", ["payment_attempt_id"]
    )
    op.create_index(
        "ix_finance_transactions_transaction_type", "finance_transactions", ["transaction_type"]
    )
    op.create_index("ix_finance_transactions_status", "finance_transactions", ["status"])
    op.create_index(
        "ix_finance_transactions_invoice_type",
        "finance_transactions",
        ["invoice_id", "transaction_type"],
    )

    op.create_table(
        "finance_refunds",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.BigInteger(), nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("payment_attempt_id", sa.BigInteger(), nullable=True),
        sa.Column("transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("idempotency_key", sa.String(160), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("provider_reference", sa.String(255), nullable=True),
        sa.Column("requested_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("processed_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("requested_at", sa.DateTime(), nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_finance_refunds_amount_positive"),
        sa.ForeignKeyConstraint(["invoice_id"], ["finance_invoices.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["payment_attempt_id"], ["payment_attempts.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["transaction_id"], ["finance_transactions.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["auth_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["processed_by_user_id"], ["auth_users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
        sa.UniqueConstraint("provider_reference"),
    )
    op.create_index("ix_finance_refunds_invoice_id", "finance_refunds", ["invoice_id"])
    op.create_index("ix_finance_refunds_order_id", "finance_refunds", ["order_id"])
    op.create_index("ix_finance_refunds_status", "finance_refunds", ["status"])
    op.create_index(
        "ix_finance_refunds_invoice_status", "finance_refunds", ["invoice_id", "status"]
    )

    op.create_table(
        "inventory_reservations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("order_item_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("released_at", sa.DateTime(), nullable=True),
        sa.Column("release_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_inventory_reservations_quantity_positive"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_item_id"], ["order_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["store_products.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_item_id"),
    )
    op.create_index("ix_inventory_reservations_order_id", "inventory_reservations", ["order_id"])
    op.create_index(
        "ix_inventory_reservations_product_id", "inventory_reservations", ["product_id"]
    )
    op.create_index("ix_inventory_reservations_status", "inventory_reservations", ["status"])
    op.create_index(
        "ix_inventory_reservations_expires_at", "inventory_reservations", ["expires_at"]
    )
    op.create_index(
        "ix_inventory_reservations_product_status",
        "inventory_reservations",
        ["product_id", "status"],
    )


def downgrade() -> None:
    op.drop_table("inventory_reservations")
    op.drop_table("finance_refunds")
    op.drop_table("finance_transactions")
    op.drop_table("payment_attempts")
    op.drop_table("commission_snapshots")
    op.drop_table("finance_invoice_items")
    op.drop_table("finance_invoices")
