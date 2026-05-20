from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.orders.enums import (
    CartStatus,
    CommissionSettingStatus,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
)


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default=CartStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )

    currency: Mapped[str] = mapped_column(String(10), default="TOMAN", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    checked_out_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_carts_user_status", "user_id", "status"),
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    cart_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("store_products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    product_name_snapshot: Mapped[str] = mapped_column(String(220), nullable=False)
    product_slug_snapshot: Mapped[str] = mapped_column(String(160), nullable=False)
    product_sku_snapshot: Mapped[str | None] = mapped_column(String(120), nullable=True)
    unit_snapshot: Mapped[str] = mapped_column(String(30), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    cart: Mapped["Cart"] = relationship(back_populates="items")

    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_items_cart_product"),
        Index("ix_cart_items_cart_store", "cart_id", "store_id"),
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    order_number: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        unique=True,
        index=True,
    )

    buyer_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default=OrderStatus.PENDING_PAYMENT.value,
        nullable=False,
        index=True,
    )

    payment_status: Mapped[str] = mapped_column(
        String(50),
        default=PaymentStatus.PENDING.value,
        nullable=False,
        index=True,
    )

    currency: Mapped[str] = mapped_column(String(10), default="TOMAN", nullable=False)

    subtotal_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    shipping_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    commission_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    seller_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    buyer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    seller_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    shipping_province_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("geo_provinces.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    shipping_county_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("geo_counties.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    shipping_city_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("geo_cities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    shipping_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    shipping_postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    shipping_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    status_history: Mapped[list["OrderStatusHistory"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_orders_buyer_status", "buyer_user_id", "status"),
        Index("ix_orders_store_status", "store_id", "status"),
        Index("ix_orders_payment_status", "payment_status"),
        Index("ix_orders_created", "created_at"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("store_products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    product_name_snapshot: Mapped[str] = mapped_column(String(220), nullable=False)
    product_slug_snapshot: Mapped[str] = mapped_column(String(160), nullable=False)
    product_sku_snapshot: Mapped[str | None] = mapped_column(String(120), nullable=True)
    unit_snapshot: Mapped[str] = mapped_column(String(30), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")

    __table_args__ = (
        Index("ix_order_items_order_store", "order_id", "store_id"),
        Index("ix_order_items_product", "product_id"),
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    method: Mapped[str] = mapped_column(
        String(50),
        default=PaymentMethod.MOCK.value,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default=PaymentStatus.PENDING.value,
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="TOMAN", nullable=False)

    provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provider_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    provider_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    order: Mapped["Order"] = relationship(back_populates="payments")

    __table_args__ = (
        Index("ix_payments_order_status", "order_id", "status"),
        Index("ix_payments_user_status", "user_id", "status"),
    )


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    changed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="status_history")

    __table_args__ = (
        Index("ix_order_status_history_order_created", "order_id", "created_at"),
    )


class CommissionSetting(Base):
    __tablename__ = "commission_settings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(180), nullable=False)

    percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    status: Mapped[str] = mapped_column(
        String(50),
        default=CommissionSettingStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )

    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    updated_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_commission_settings_status_default", "status", "is_default"),
    )