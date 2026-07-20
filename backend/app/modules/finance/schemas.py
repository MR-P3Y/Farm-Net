from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.common.money import toman_currency


class FinalPriceProposalIn(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: str = Field(default="TOMAN", min_length=5, max_length=10)
    description: str = Field(min_length=3, max_length=500)

    model_config = {"extra": "forbid"}
    _currency = field_validator("currency", mode="before")(toman_currency)

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value):
        if isinstance(value, str):
            return value.strip() or None
        return value


class FinalPriceDecisionIn(BaseModel):
    decision: str = Field(pattern="^(accept|reject)$")

    model_config = {"extra": "forbid"}


class FinalPriceProposalOut(BaseModel):
    id: int
    source_type: str
    source_id: int
    version: int
    amount: Decimal
    currency: str
    description: str
    status: str
    proposed_by_user_id: int
    decided_by_user_id: int | None = None
    proposed_at: datetime
    decided_at: datetime | None = None
    invoice_id: int | None = None


class LedgerReconciliationOut(BaseModel):
    successful_payment_transactions: int
    successful_refund_transactions: int
    posted_payment_journals: int
    posted_refund_journals: int
    missing_payment_transaction_ids: list[int]
    missing_refund_transaction_ids: list[int]
    unbalanced_journal_ids: list[int]
    entry_mismatch_journal_ids: list[int]

    @property
    def is_clean(self) -> bool:
        return not (
            self.missing_payment_transaction_ids
            or self.missing_refund_transaction_ids
            or self.unbalanced_journal_ids
            or self.entry_mismatch_journal_ids
        )


class AdminLedgerJournalOut(BaseModel):
    id: int
    journal_number: str
    event_type: str
    source_type: str
    source_id: int
    status: str
    currency: str
    total_debit: Decimal
    total_credit: Decimal
    trace_id: str
    posted_at: datetime


class AdminWalletAccountOut(BaseModel):
    id: int
    owner_user_id: int | None
    account_code: str
    purpose: str
    currency: str
    status: str
    created_at: datetime


class WalletBalanceOut(BaseModel):
    currency: str
    pending_amount: Decimal
    available_amount: Decimal
    reserved_amount: Decimal


class OwnInvoiceOut(BaseModel):
    id: int
    invoice_number: str
    source_type: str
    source_id: int
    status: str
    currency: str
    subtotal_amount: Decimal
    discount_amount: Decimal
    surcharge_amount: Decimal
    total_amount: Decimal
    issued_at: datetime
    paid_at: datetime | None
    refunded_at: datetime | None


class SettlementCreateIn(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: str = Field(default="TOMAN", min_length=5, max_length=10)
    idempotency_key: str = Field(min_length=8, max_length=180)
    note: str | None = Field(default=None, max_length=500)

    model_config = {"extra": "forbid"}
    _currency = field_validator("currency", mode="before")(toman_currency)


class SettlementDecisionIn(BaseModel):
    decision: str = Field(pattern="^(approve|reject)$")
    admin_note: str | None = Field(default=None, max_length=1000)

    model_config = {"extra": "forbid"}


class SettlementOut(BaseModel):
    id: int
    requester_user_id: int
    amount: Decimal
    currency: str
    status: str
    note: str | None
    admin_note: str | None
    requested_at: datetime
    decided_at: datetime | None
    simulated_completed_at: datetime | None


class AdjustmentCreateIn(BaseModel):
    provider_user_id: int = Field(ge=1)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    direction: str = Field(pattern="^(credit|debit)$")
    currency: str = Field(default="TOMAN", min_length=5, max_length=10)
    idempotency_key: str = Field(min_length=8, max_length=180)
    reason: str = Field(min_length=10, max_length=1000)

    model_config = {"extra": "forbid"}
    _currency = field_validator("currency", mode="before")(toman_currency)

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value):
        return value.strip() if isinstance(value, str) else value
