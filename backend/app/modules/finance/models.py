from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.money import CurrencyCode
from app.db.base import Base
from app.modules.finance.enums import AccountStatus, LedgerStatus
from app.modules.finance.enums import BillingInvoiceStatus, CommissionPolicyStatus


class CommissionPolicy(Base):
    __tablename__ = "finance_commission_policies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    default_scope: Mapped[str | None] = mapped_column(String(50))
    percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=CommissionPolicyStatus.ACTIVE.value, nullable=False, index=True
    )
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("default_scope", name="uq_commission_policy_default_scope"),
        CheckConstraint("percent >= 0 AND percent <= 100", name="ck_commission_policy_percent"),
        CheckConstraint(
            "(is_default = 0 AND default_scope IS NULL) OR "
            "(is_default = 1 AND default_scope = source_type)",
            name="ck_commission_policy_default_scope",
        ),
        Index("ix_commission_policy_source_default", "source_type", "status", "is_default"),
    )


class BillingInvoice(Base):
    __tablename__ = "finance_billing_invoices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(70), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    legacy_invoice_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("finance_invoices.id", ondelete="RESTRICT"), unique=True, index=True
    )
    payer_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    provider_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default=BillingInvoiceStatus.PAYMENT_PENDING.value, nullable=False, index=True
    )
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    subtotal_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    surcharge_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    platform_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    provider_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    items: Mapped[list["BillingInvoiceItem"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )
    commission_snapshot: Mapped["BillingCommissionSnapshot | None"] = relationship(
        back_populates="invoice", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("source_type", "source_id", name="uq_billing_invoice_source"),
        CheckConstraint("currency = 'TOMAN'", name="ck_billing_invoice_currency_toman"),
        CheckConstraint("subtotal_amount >= 0", name="ck_billing_invoice_subtotal"),
        CheckConstraint("discount_amount >= 0", name="ck_billing_invoice_discount"),
        CheckConstraint("surcharge_amount >= 0", name="ck_billing_invoice_surcharge"),
        CheckConstraint("total_amount > 0", name="ck_billing_invoice_total"),
        CheckConstraint("platform_amount >= 0", name="ck_billing_invoice_platform"),
        CheckConstraint("provider_amount >= 0", name="ck_billing_invoice_provider"),
        CheckConstraint(
            "platform_amount + provider_amount = total_amount",
            name="ck_billing_invoice_split_total",
        ),
        Index("ix_billing_invoice_payer_status", "payer_user_id", "status"),
        Index("ix_billing_invoice_provider_status", "provider_user_id", "status"),
    )


class BillingInvoiceItem(Base):
    __tablename__ = "finance_billing_invoice_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("finance_billing_invoices.id", ondelete="RESTRICT"), index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    source_item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_item_id: Mapped[int | None] = mapped_column(BigInteger)
    title_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    description_snapshot: Mapped[str | None] = mapped_column(Text)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    unit_snapshot: Mapped[str] = mapped_column(String(40), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    invoice: Mapped[BillingInvoice] = relationship(back_populates="items")

    __table_args__ = (
        UniqueConstraint("invoice_id", "sequence", name="uq_billing_invoice_item_sequence"),
        CheckConstraint("sequence > 0", name="ck_billing_item_sequence"),
        CheckConstraint("quantity > 0", name="ck_billing_item_quantity"),
        CheckConstraint("unit_price >= 0", name="ck_billing_item_unit_price"),
        CheckConstraint("line_total >= 0", name="ck_billing_item_line_total"),
    )


class BillingCommissionSnapshot(Base):
    __tablename__ = "finance_billing_commission_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("finance_billing_invoices.id", ondelete="RESTRICT"), unique=True
    )
    policy_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("finance_commission_policies.id", ondelete="SET NULL"), index=True
    )
    legacy_snapshot_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("commission_snapshots.id", ondelete="RESTRICT"), unique=True
    )
    calculation_type: Mapped[str] = mapped_column(String(30), nullable=False)
    percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    base_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    platform_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    provider_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    invoice: Mapped[BillingInvoice] = relationship(back_populates="commission_snapshot")

    __table_args__ = (
        CheckConstraint("percent >= 0 AND percent <= 100", name="ck_billing_commission_percent"),
        CheckConstraint("base_amount >= 0", name="ck_billing_commission_base"),
        CheckConstraint("platform_amount >= 0", name="ck_billing_commission_platform"),
        CheckConstraint("provider_amount >= 0", name="ck_billing_commission_provider"),
    )


class WalletAccount(Base):
    __tablename__ = "finance_wallet_accounts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), index=True
    )
    account_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    account_kind: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(
        String(10), default=CurrencyCode.TOMAN.value, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default=AccountStatus.ACTIVE.value, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)

    entries: Mapped[list["LedgerEntry"]] = relationship(back_populates="account")

    __table_args__ = (
        UniqueConstraint(
            "owner_user_id", "purpose", "currency", name="uq_wallet_owner_purpose_currency"
        ),
        CheckConstraint("currency = 'TOMAN'", name="ck_wallet_accounts_currency_toman"),
        Index("ix_wallet_accounts_owner_status", "owner_user_id", "status"),
    )


class LedgerTransaction(Base):
    __tablename__ = "finance_ledger_transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    journal_number: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    legacy_transaction_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("finance_transactions.id", ondelete="RESTRICT"),
        unique=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20), default=LedgerStatus.POSTED.value, nullable=False, index=True
    )
    currency: Mapped[str] = mapped_column(
        String(10), default=CurrencyCode.TOMAN.value, nullable=False
    )
    total_debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    reversal_of_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("finance_ledger_transactions.id", ondelete="RESTRICT"),
        index=True,
    )
    actor_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="SET NULL"), index=True
    )
    trace_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    posted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    entries: Mapped[list["LedgerEntry"]] = relationship(
        back_populates="transaction", cascade="all, delete-orphan"
    )
    reversal_of: Mapped["LedgerTransaction | None"] = relationship(
        remote_side="LedgerTransaction.id"
    )

    __table_args__ = (
        UniqueConstraint("reversal_of_id", name="uq_ledger_transaction_reversal"),
        CheckConstraint("currency = 'TOMAN'", name="ck_ledger_transactions_currency_toman"),
        CheckConstraint("total_debit > 0", name="ck_ledger_transactions_debit_positive"),
        CheckConstraint("total_credit > 0", name="ck_ledger_transactions_credit_positive"),
        CheckConstraint(
            "total_debit = total_credit", name="ck_ledger_transactions_balanced_totals"
        ),
        Index("ix_ledger_transactions_source", "source_type", "source_id"),
        Index("ix_ledger_transactions_posted", "posted_at", "id"),
    )


class LedgerEntry(Base):
    __tablename__ = "finance_ledger_entries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("finance_ledger_transactions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("finance_wallet_accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(10), default=CurrencyCode.TOMAN.value, nullable=False
    )
    memo: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    transaction: Mapped[LedgerTransaction] = relationship(back_populates="entries")
    account: Mapped[WalletAccount] = relationship(back_populates="entries")

    __table_args__ = (
        UniqueConstraint("transaction_id", "sequence", name="uq_ledger_entry_sequence"),
        CheckConstraint("sequence > 0", name="ck_ledger_entries_sequence_positive"),
        CheckConstraint("side IN ('debit', 'credit')", name="ck_ledger_entries_side"),
        CheckConstraint("amount > 0", name="ck_ledger_entries_amount_positive"),
        CheckConstraint("currency = 'TOMAN'", name="ck_ledger_entries_currency_toman"),
        Index("ix_ledger_entries_account_created", "account_id", "created_at"),
    )


def _reject_posted_ledger_mutation(_mapper, _connection, target) -> None:
    raise RuntimeError(f"Posted ledger record {target.__class__.__name__} is immutable")


for _model in (LedgerTransaction, LedgerEntry, BillingInvoiceItem, BillingCommissionSnapshot):
    event.listen(_model, "before_update", _reject_posted_ledger_mutation)
    event.listen(_model, "before_delete", _reject_posted_ledger_mutation)
