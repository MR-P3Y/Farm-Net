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
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FarmMeasurementUnit(Base):
    __tablename__ = "farm_measurement_units"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(30), nullable=False)
    dimension: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    factor_to_base: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    is_base: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("factor_to_base > 0", name="ck_farm_measurement_units_factor_positive"),
        Index(
            "ix_farm_measurement_units_dimension_active_sort",
            "dimension",
            "is_active",
            "sort_order",
        ),
    )


class FarmCropCategory(Base):
    __tablename__ = "farm_crop_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(140), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    crops: Mapped[list["FarmCrop"]] = relationship(back_populates="category")

    __table_args__ = (
        Index("ix_farm_crop_categories_active_sort", "is_active", "sort_order"),
    )


class FarmCrop(Base):
    __tablename__ = "farm_crops"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("farm_crop_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    scientific_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_cycle_type: Mapped[str] = mapped_column(
        String(30),
        default="annual",
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    category: Mapped["FarmCropCategory"] = relationship(back_populates="crops")
    varieties: Mapped[list["FarmCropVariety"]] = relationship(back_populates="crop")

    __table_args__ = (
        UniqueConstraint("scientific_name", name="uq_farm_crops_scientific_name"),
        CheckConstraint(
            "default_cycle_type in ('annual', 'perennial')",
            name="ck_farm_crops_cycle_type",
        ),
        Index("ix_farm_crops_category_active_sort", "category_id", "is_active", "sort_order"),
    )


class FarmCropVariety(Base):
    __tablename__ = "farm_crop_varieties"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("farm_crops.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    scientific_name: Mapped[str | None] = mapped_column(String(220), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    crop: Mapped["FarmCrop"] = relationship(back_populates="varieties")

    __table_args__ = (
        UniqueConstraint("crop_id", "code", name="uq_farm_crop_varieties_crop_code"),
        Index("ix_farm_crop_varieties_crop_active_sort", "crop_id", "is_active", "sort_order"),
    )
