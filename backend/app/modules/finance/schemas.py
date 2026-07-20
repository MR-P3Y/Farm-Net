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
