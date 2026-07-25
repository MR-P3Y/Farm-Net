from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.orders import models as order_models  # noqa: F401
from app.modules.rentals import models as rental_models  # noqa: F401
from app.modules.finance import models as finance_models  # noqa: F401
from app.modules.subscriptions.enums import (
    EntitlementSource,
    FeatureStatus,
    PlanStatus,
    SubscriptionPeriodStatus,
    SubscriptionStatus,
    UsageReservationStatus,
)


class BillingPlan(Base):
    __tablename__ = "billing_plans"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default=PlanStatus.DRAFT.value, nullable=False, index=True
    )
    billing_period: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_days: Mapped[int | None] = mapped_column(Integer)
    price_toman: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="TOMAN", nullable=False)
    is_default_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    effective_from: Mapped[datetime | None] = mapped_column(DateTime)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    features: Mapped[list["BillingPlanFeature"]] = relationship(back_populates="plan")
    subscriptions: Mapped[list["BillingSubscription"]] = relationship(back_populates="plan")

    __table_args__ = (
        UniqueConstraint("code", "version", name="uq_billing_plan_code_version"),
        CheckConstraint("status IN ('draft', 'active', 'retired')", name="ck_billing_plans_status"),
        CheckConstraint(
            "billing_period IN ('free', 'monthly', 'yearly', 'custom')",
            name="ck_billing_plans_period",
        ),
        CheckConstraint("currency = 'TOMAN'", name="ck_billing_plans_currency_toman"),
        CheckConstraint("price_toman >= 0", name="ck_billing_plans_price_nonnegative"),
        CheckConstraint("version > 0", name="ck_billing_plans_version_positive"),
        CheckConstraint(
            "(billing_period = 'free' AND price_toman = 0) OR billing_period <> 'free'",
            name="ck_billing_plans_free_price",
        ),
        CheckConstraint(
            "(billing_period = 'custom' AND duration_days > 0) OR "
            "(billing_period <> 'custom' AND duration_days IS NULL)",
            name="ck_billing_plans_custom_duration",
        ),
        CheckConstraint(
            "is_default_free = 0 OR (billing_period = 'free' AND price_toman = 0)",
            name="ck_billing_plans_default_free",
        ),
        CheckConstraint(
            "effective_until IS NULL OR effective_from IS NULL OR effective_until > effective_from",
            name="ck_billing_plans_effective_range",
        ),
        Index("ix_billing_plans_status_period", "status", "billing_period"),
    )


class BillingFeature(Base):
    __tablename__ = "billing_features"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    module: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    value_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(40))
    is_metered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_safety_exempt: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=FeatureStatus.ACTIVE.value, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    plan_values: Mapped[list["BillingPlanFeature"]] = relationship(back_populates="feature")

    __table_args__ = (
        CheckConstraint(
            "value_kind IN ('boolean', 'integer', 'decimal', 'string', 'json')",
            name="ck_billing_features_value_kind",
        ),
        CheckConstraint("status IN ('active', 'retired')", name="ck_billing_features_status"),
        CheckConstraint(
            "is_safety_exempt = 0 OR is_metered = 0",
            name="ck_billing_features_safety_not_metered",
        ),
        Index("ix_billing_features_module_status", "module", "status"),
    )


class BillingPlanFeature(Base):
    __tablename__ = "billing_plan_features"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("billing_plans.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    feature_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("billing_features.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_unlimited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    boolean_value: Mapped[bool | None] = mapped_column(Boolean)
    numeric_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    string_value: Mapped[str | None] = mapped_column(String(500))
    json_value: Mapped[dict | list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    plan: Mapped[BillingPlan] = relationship(back_populates="features")
    feature: Mapped[BillingFeature] = relationship(back_populates="plan_values")

    __table_args__ = (
        UniqueConstraint("plan_id", "feature_id", name="uq_billing_plan_feature"),
        CheckConstraint(
            "numeric_value IS NULL OR numeric_value >= 0",
            name="ck_billing_plan_features_numeric_nonnegative",
        ),
        CheckConstraint(
            "is_unlimited = 0 OR numeric_value IS NULL",
            name="ck_billing_plan_features_unlimited_no_numeric",
        ),
    )


class BillingSubscription(Base):
    __tablename__ = "billing_subscriptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    plan_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("billing_plans.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default=SubscriptionStatus.PENDING.value, nullable=False, index=True
    )
    starts_at: Mapped[datetime | None] = mapped_column(DateTime)
    current_period_starts_at: Mapped[datetime | None] = mapped_column(DateTime)
    current_period_ends_at: Mapped[datetime | None] = mapped_column(DateTime)
    grace_ends_at: Mapped[datetime | None] = mapped_column(DateTime)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancellation_reason: Mapped[str | None] = mapped_column(String(500))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    plan: Mapped[BillingPlan] = relationship(back_populates="subscriptions")
    periods: Mapped[list["BillingSubscriptionPeriod"]] = relationship(back_populates="subscription")
    entitlements: Mapped[list["BillingEntitlement"]] = relationship(back_populates="subscription")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'active', 'grace', 'cancelled', 'expired')",
            name="ck_billing_subscriptions_status",
        ),
        CheckConstraint("version > 0", name="ck_billing_subscriptions_version_positive"),
        CheckConstraint(
            "current_period_ends_at IS NULL OR current_period_starts_at IS NULL OR "
            "current_period_ends_at > current_period_starts_at",
            name="ck_billing_subscriptions_period_range",
        ),
        CheckConstraint(
            "grace_ends_at IS NULL OR current_period_ends_at IS NULL OR "
            "grace_ends_at >= current_period_ends_at",
            name="ck_billing_subscriptions_grace_range",
        ),
        CheckConstraint(
            "(status IN ('cancelled', 'expired') AND ended_at IS NOT NULL) OR "
            "(status NOT IN ('cancelled', 'expired') AND ended_at IS NULL)",
            name="ck_billing_subscriptions_end_state",
        ),
        CheckConstraint(
            "cancelled_at IS NULL OR cancellation_reason IS NOT NULL",
            name="ck_billing_subscriptions_cancel_reason",
        ),
        Index("ix_billing_subscriptions_user_status", "user_id", "status"),
        Index("ix_billing_subscriptions_period_end", "status", "current_period_ends_at"),
    )


class BillingSubscriptionPeriod(Base):
    __tablename__ = "billing_subscription_periods"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("billing_subscriptions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=SubscriptionPeriodStatus.PENDING.value, nullable=False
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    invoice_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("finance_billing_invoices.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    plan_code_snapshot: Mapped[str] = mapped_column(String(80), nullable=False)
    plan_version_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    price_toman_snapshot: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="TOMAN", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    subscription: Mapped[BillingSubscription] = relationship(back_populates="periods")
    entitlements: Mapped[list["BillingEntitlement"]] = relationship(back_populates="period")

    __table_args__ = (
        UniqueConstraint(
            "subscription_id", "sequence", name="uq_billing_subscription_period_sequence"
        ),
        UniqueConstraint("invoice_id", name="uq_billing_subscription_period_invoice"),
        CheckConstraint("sequence > 0", name="ck_billing_subscription_period_sequence"),
        CheckConstraint(
            "status IN ('pending', 'active', 'closed', 'void')",
            name="ck_billing_subscription_period_status",
        ),
        CheckConstraint("ends_at > starts_at", name="ck_billing_subscription_period_range"),
        CheckConstraint("plan_version_snapshot > 0", name="ck_billing_period_plan_version"),
        CheckConstraint("price_toman_snapshot >= 0", name="ck_billing_period_price_nonnegative"),
        CheckConstraint("currency = 'TOMAN'", name="ck_billing_period_currency_toman"),
        Index("ix_billing_subscription_period_dates", "starts_at", "ends_at"),
    )


class BillingEntitlement(Base):
    __tablename__ = "billing_entitlements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    subscription_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("billing_subscriptions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    period_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("billing_subscription_periods.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    feature_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("billing_features.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    feature_code_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)
    source: Mapped[str] = mapped_column(
        String(20), default=EntitlementSource.PLAN.value, nullable=False
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_unlimited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    limit_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    policy_value: Mapped[dict | list | None] = mapped_column(JSON)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    subscription: Mapped[BillingSubscription] = relationship(back_populates="entitlements")
    period: Mapped[BillingSubscriptionPeriod] = relationship(back_populates="entitlements")
    usage: Mapped["BillingFeatureUsage | None"] = relationship(
        back_populates="entitlement", uselist=False
    )

    __table_args__ = (
        UniqueConstraint("period_id", "feature_id", name="uq_billing_entitlement_period_feature"),
        CheckConstraint(
            "source IN ('plan', 'addon', 'admin')", name="ck_billing_entitlements_source"
        ),
        CheckConstraint(
            "limit_value IS NULL OR limit_value >= 0",
            name="ck_billing_entitlements_limit_nonnegative",
        ),
        CheckConstraint(
            "is_unlimited = 0 OR limit_value IS NULL",
            name="ck_billing_entitlements_unlimited_no_limit",
        ),
        CheckConstraint("ends_at > starts_at", name="ck_billing_entitlements_range"),
        Index("ix_billing_entitlements_user_feature", "user_id", "feature_code_snapshot"),
    )


class BillingFeatureUsage(Base):
    __tablename__ = "billing_feature_usage"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entitlement_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("billing_entitlements.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    period_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("billing_subscription_periods.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    feature_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("billing_features.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    used_value: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), default=Decimal("0"), nullable=False
    )
    reserved_value: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), default=Decimal("0"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    entitlement: Mapped[BillingEntitlement] = relationship(back_populates="usage")
    reservations: Mapped[list["BillingUsageReservation"]] = relationship(back_populates="usage")

    __table_args__ = (
        UniqueConstraint(
            "user_id", "period_id", "feature_id", name="uq_billing_feature_usage_scope"
        ),
        CheckConstraint("used_value >= 0", name="ck_billing_feature_usage_used"),
        CheckConstraint("reserved_value >= 0", name="ck_billing_feature_usage_reserved"),
        CheckConstraint("version > 0", name="ck_billing_feature_usage_version"),
        Index("ix_billing_feature_usage_user_period", "user_id", "period_id"),
    )


class BillingUsageReservation(Base):
    __tablename__ = "billing_usage_reservations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    usage_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("billing_feature_usage.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    feature_code_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=UsageReservationStatus.RESERVED.value, nullable=False, index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime)
    released_at: Mapped[datetime | None] = mapped_column(DateTime)
    release_reason: Mapped[str | None] = mapped_column(String(500))
    context: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    usage: Mapped[BillingFeatureUsage] = relationship(back_populates="reservations")

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_billing_usage_reservation_amount"),
        CheckConstraint(
            "status IN ('reserved', 'finalized', 'released', 'expired')",
            name="ck_billing_usage_reservation_status",
        ),
        CheckConstraint(
            "(status = 'reserved' AND finalized_at IS NULL AND released_at IS NULL) OR "
            "(status = 'finalized' AND finalized_at IS NOT NULL AND released_at IS NULL) OR "
            "(status IN ('released', 'expired') AND finalized_at IS NULL AND "
            "released_at IS NOT NULL)",
            name="ck_billing_usage_reservation_terminal_state",
        ),
        Index("ix_billing_usage_reservations_expiry", "status", "expires_at"),
    )


class BillingSubscriptionPaymentAttempt(Base):
    __tablename__ = "billing_subscription_payment_attempts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("billing_subscriptions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    invoice_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("finance_billing_invoices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    amount_toman: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="TOMAN", nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    provider_authority: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True
    )
    provider_reference: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True
    )
    redirect_url: Mapped[str | None] = mapped_column(Text)
    failure_code: Mapped[str | None] = mapped_column(String(100))
    failure_message: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint("provider IN ('mock', 'zarinpal')", name="ck_subscription_payment_provider"),
        CheckConstraint(
            "status IN ('pending', 'redirected', 'verifying', 'succeeded', 'failed', 'cancelled')",
            name="ck_subscription_payment_status",
        ),
        CheckConstraint("amount_toman > 0", name="ck_subscription_payment_amount"),
        CheckConstraint("currency = 'TOMAN'", name="ck_subscription_payment_currency"),
        Index("ix_subscription_payment_user_status", "user_id", "status"),
    )
