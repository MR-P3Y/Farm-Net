from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class CurrencyCode(StrEnum):
    TOMAN = "TOMAN"


class BillableSourceType(StrEnum):
    PRODUCT_ORDER = "product_order"
    SERVICE_REQUEST = "service_request"
    RENTAL_REQUEST = "rental_request"
    CONSULTATION_REQUEST = "consultation_request"


class FinancialEventType(StrEnum):
    INVOICE = "invoice"
    PAYMENT = "payment"
    RELEASE = "release"
    CANCELLATION = "cancellation"
    REFUND = "refund"
    REVERSAL = "reversal"
    SETTLEMENT = "settlement"


def toman_currency(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().upper()
    if normalized != CurrencyCode.TOMAN.value:
        raise ValueError("Currency must be TOMAN (Iranian toman)")
    return normalized


class BillableSourceRef(BaseModel):
    source_type: BillableSourceType
    source_id: int = Field(ge=1)
    payer_user_id: int = Field(ge=1)
    provider_user_id: int = Field(ge=1)
    currency: CurrencyCode = CurrencyCode.TOMAN

    @field_validator("currency", mode="before")
    @classmethod
    def validate_currency(cls, value):
        return toman_currency(value)
