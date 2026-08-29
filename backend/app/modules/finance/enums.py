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
    ADJUSTMENT_CLEARING = "adjustment_clearing"


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


class BillingInvoiceStatus(StrEnum):
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUND_PENDING = "refund_pending"
    REFUNDED = "refunded"


class BillingPaymentAttemptStatus(StrEnum):
    PENDING = "pending"
    REDIRECTED = "redirected"
    VERIFYING = "verifying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BillingRefundStatus(StrEnum):
    REQUESTED = "requested"
    APPROVED = "approved"
    SUCCEEDED = "succeeded"
    REJECTED = "rejected"


class CommissionPolicyStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class FinalPriceProposalStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class RentalFinancialTermsStatus(StrEnum):
    UNFUNDED = "unfunded"
    CANCELLED_UNFUNDED = "cancelled_unfunded"
    OPERATIONALLY_COMPLETED_UNFUNDED = "operationally_completed_unfunded"


class SettlementStatus(StrEnum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    SIMULATED_COMPLETED = "simulated_completed"
