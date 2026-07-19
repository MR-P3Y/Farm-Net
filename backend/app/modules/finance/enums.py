from enum import StrEnum


class AccountKind(StrEnum):
    ASSET = "asset"
    LIABILITY = "liability"
    REVENUE = "revenue"
    EXPENSE = "expense"
    EQUITY = "equity"


class AccountPurpose(StrEnum):
    PROVIDER_PENDING = "provider_pending"
    PROVIDER_AVAILABLE = "provider_available"
    PROVIDER_RESERVED = "provider_reserved"
    CUSTOMER_FUNDS = "customer_funds"
    PLATFORM_CASH = "platform_cash"
    PLATFORM_REVENUE = "platform_revenue"
    DEPOSIT_LIABILITY = "deposit_liability"
    REFUND_CLEARING = "refund_clearing"
    PAYOUT_CLEARING = "payout_clearing"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


class EntrySide(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class LedgerStatus(StrEnum):
    POSTED = "posted"
    REVERSED = "reversed"
