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
    invoice_status: str | None = None
    refund_id: int | None = None
    refund_status: str | None = None
    refund_review_required: bool | None = None


class BillingRefundCreateIn(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)
    idempotency_key: str = Field(min_length=8, max_length=180)

    model_config = {"extra": "forbid"}

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value):
        return value.strip() if isinstance(value, str) else value


class BillingRefundDecisionIn(BaseModel):
    decision: str = Field(pattern="^(approve|reject)$")
    admin_note: str | None = Field(default=None, max_length=1000)

    model_config = {"extra": "forbid"}

    @field_validator("admin_note", mode="before")
    @classmethod
    def normalize_admin_note(cls, value):
        if isinstance(value, str):
            return value.strip() or None
        return value


class BillingRefundCompleteIn(BaseModel):
    provider_reference: str = Field(min_length=3, max_length=255)

    model_config = {"extra": "forbid"}


class BillingRefundOut(BaseModel):
    id: int
    invoice_id: int
    payment_attempt_id: int
    source_type: str
    source_id: int
    payer_user_id: int
    provider_user_id: int
    status: str
    amount_toman: Decimal
    currency: str
    reason: str
    review_required: bool
    provider_reference: str | None = None
    requested_by_user_id: int
    decided_by_user_id: int | None = None
    admin_note: str | None = None
    requested_at: datetime
    decided_at: datetime | None = None
    processed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CommissionPolicyUpdateIn(BaseModel):
    percent: Decimal = Field(ge=0, lt=100, max_digits=5, decimal_places=2)

    model_config = {"extra": "forbid"}


class CommissionPolicyOut(BaseModel):
    id: int
    code: str
    title: str
    source_type: str
    percent: Decimal
    status: str
    is_default: bool
    created_at: datetime
    updated_at: datetime


class InvoicePaymentCheckoutIn(BaseModel):
    provider: str = Field(pattern="^(mock|zarinpal)$")
    idempotency_key: str = Field(min_length=8, max_length=180)

    model_config = {"extra": "forbid"}


class InvoicePaymentVerifyIn(BaseModel):
    payment_attempt_id: int = Field(ge=1)
    provider_token: str = Field(min_length=1, max_length=255)

    model_config = {"extra": "forbid"}


class BillingPaymentAttemptOut(BaseModel):
    id: int
    invoice_id: int
    source_type: str
    source_id: int
    user_id: int
    provider: str
    status: str
    amount_toman: Decimal
    currency: str
    redirect_url: str | None = None
    failure_code: str | None = None
    failure_message: str | None = None
    expires_at: datetime
    verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


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
