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
from app.modules.products.enums import ProductStatus, ProductUnit


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("product_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(140), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    parent: Mapped["ProductCategory | None"] = relationship(
        remote_side="ProductCategory.id",
        back_populates="children",
    )
    children: Mapped[list["ProductCategory"]] = relationship(
        back_populates="parent",
    )

    products: Mapped[list["StoreProduct"]] = relationship(
        back_populates="category",
    )

    __table_args__ = (
        Index("ix_product_categories_parent_active", "parent_id", "is_active"),
        Index("ix_product_categories_sort", "sort_order", "name"),
    )


class StoreProduct(Base):
    __tablename__ = "store_products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("product_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(220), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(160), nullable=False, index=True)

    short_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    sku: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)

    status: Mapped[str] = mapped_column(
        String(50),
        default=ProductStatus.DRAFT.value,
        nullable=False,
        index=True,
    )

    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    compare_at_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="TOMAN", nullable=False)

    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unit: Mapped[str] = mapped_column(
        String(30),
        default=ProductUnit.PIECE.value,
        nullable=False,
        index=True,
    )

    min_order_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_order_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    suspended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    suspended_by: Mapped[int | None] = mapped_column(
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
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    category: Mapped["ProductCategory | None"] = relationship(
        back_populates="products",
    )
    store = relationship("Store")

    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    status_history: Mapped[list["ProductStatusHistory"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("store_id", "slug", name="uq_store_products_store_slug"),
        UniqueConstraint("store_id", "sku", name="uq_store_products_store_sku"),
        Index("ix_store_products_store_status", "store_id", "status"),
        Index("ix_store_products_public_lookup", "status", "deleted_at", "is_active"),
        Index("ix_store_products_category_status", "category_id", "status"),
        Index("ix_store_products_price", "price"),
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("store_products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    media_file_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("media_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(255), nullable=True)

    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    product: Mapped["StoreProduct"] = relationship(back_populates="images")

    __table_args__ = (
        Index("ix_product_images_product_sort", "product_id", "sort_order"),
        Index("ix_product_images_product_primary", "product_id", "is_primary"),
    )


class ProductStatusHistory(Base):
    __tablename__ = "product_status_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("store_products.id", ondelete="CASCADE"),
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

    product: Mapped["StoreProduct"] = relationship(back_populates="status_history")

    __table_args__ = (
        Index("ix_product_status_history_product_created", "product_id", "created_at"),
    )
