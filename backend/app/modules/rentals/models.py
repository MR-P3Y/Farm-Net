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
from app.modules.rentals.enums import (
    LessorStatus,
    RentalEquipmentStatus,
    RentalOperatorMode,
    RentalRequestStatus,
)


class RentalCategory(Base):
    __tablename__ = "rental_categories"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("rental_categories.id", ondelete="SET NULL"), index=True
    )
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(180), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    parent: Mapped["RentalCategory | None"] = relationship(
        remote_side="RentalCategory.id", back_populates="children"
    )
    children: Mapped[list["RentalCategory"]] = relationship(back_populates="parent")
    equipment: Mapped[list["RentalEquipment"]] = relationship(back_populates="category")
    __table_args__ = (Index("ix_rental_categories_active_sort", "is_active", "sort_order"),)


class LessorProfile(Base):
    __tablename__ = "rental_lessor_profiles"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="CASCADE"), unique=True, index=True
    )
    display_name: Mapped[str | None] = mapped_column(String(150))
    bio: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(30))
    province_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    city_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    address_text: Mapped[str | None] = mapped_column(Text)
    avatar_media_file_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("media_files.id", ondelete="SET NULL"), index=True
    )
    status: Mapped[str] = mapped_column(String(50), default=LessorStatus.DRAFT.value, index=True)
    admin_note: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime)
    approved_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    equipment: Mapped[list["RentalEquipment"]] = relationship(back_populates="lessor_profile")
    requests: Mapped[list["RentalRequest"]] = relationship(back_populates="lessor_profile")
    __table_args__ = (
        Index("ix_rental_lessor_status_deleted", "status", "deleted_at"),
        Index("ix_rental_lessor_geo", "province_id", "city_id"),
    )


class RentalEquipment(Base):
    __tablename__ = "rental_equipment"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    lessor_profile_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("rental_lessor_profiles.id", ondelete="CASCADE"), index=True
    )
    category_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("rental_categories.id", ondelete="SET NULL"), index=True
    )
    title: Mapped[str] = mapped_column(String(220), index=True)
    slug: Mapped[str] = mapped_column(String(180))
    description: Mapped[str | None] = mapped_column(Text)
    manufacturer: Mapped[str | None] = mapped_column(String(120))
    model_name: Mapped[str | None] = mapped_column(String(120))
    production_year: Mapped[int | None] = mapped_column(Integer)
    operator_mode: Mapped[str] = mapped_column(
        String(40), default=RentalOperatorMode.WITHOUT_OPERATOR.value, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default=RentalEquipmentStatus.DRAFT.value, index=True
    )
    province_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    city_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    address_text: Mapped[str | None] = mapped_column(Text)
    delivery_available: Mapped[bool] = mapped_column(Boolean, default=False)
    delivery_terms: Mapped[str | None] = mapped_column(Text)
    security_deposit_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(10), default="TOMAN")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    admin_note: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime)
    approved_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    lessor_profile: Mapped["LessorProfile"] = relationship(back_populates="equipment")
    category: Mapped["RentalCategory | None"] = relationship(back_populates="equipment")
    media: Mapped[list["RentalEquipmentMedia"]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan"
    )
    pricing_rules: Mapped[list["RentalPricingRule"]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan"
    )
    availability_blocks: Mapped[list["RentalAvailabilityBlock"]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan"
    )
    requests: Mapped[list["RentalRequest"]] = relationship(back_populates="equipment")
    __table_args__ = (
        UniqueConstraint("lessor_profile_id", "slug", name="uq_rental_equipment_lessor_slug"),
        CheckConstraint(
            "security_deposit_amount IS NULL OR security_deposit_amount >= 0",
            name="ck_rental_equipment_deposit_nonnegative",
        ),
        Index("ix_rental_equipment_public", "status", "is_active", "deleted_at"),
        Index("ix_rental_equipment_geo", "province_id", "city_id"),
    )


class RentalEquipmentMedia(Base):
    __tablename__ = "rental_equipment_media"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("rental_equipment.id", ondelete="CASCADE"), index=True
    )
    media_file_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("media_files.id", ondelete="CASCADE"), index=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    alt_text: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    equipment: Mapped["RentalEquipment"] = relationship(back_populates="media")
    __table_args__ = (
        UniqueConstraint("equipment_id", "media_file_id", name="uq_rental_equipment_media_file"),
        Index("ix_rental_equipment_media_sort", "equipment_id", "sort_order"),
    )


class RentalPricingRule(Base):
    __tablename__ = "rental_pricing_rules"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("rental_equipment.id", ondelete="CASCADE"), index=True
    )
    unit: Mapped[str] = mapped_column(String(30), index=True)
    operator_included: Mapped[bool] = mapped_column(Boolean, default=False)
    price_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    minimum_units: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=1)
    currency: Mapped[str] = mapped_column(String(10), default="TOMAN")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    equipment: Mapped["RentalEquipment"] = relationship(back_populates="pricing_rules")
    __table_args__ = (
        UniqueConstraint(
            "equipment_id",
            "unit",
            "operator_included",
            name="uq_rental_pricing_equipment_unit_operator",
        ),
        CheckConstraint("price_amount > 0", name="ck_rental_pricing_price_positive"),
        CheckConstraint("minimum_units > 0", name="ck_rental_pricing_minimum_positive"),
    )


class RentalAvailabilityBlock(Base):
    __tablename__ = "rental_availability_blocks"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("rental_equipment.id", ondelete="CASCADE"), index=True
    )
    block_type: Mapped[str] = mapped_column(String(30), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    note: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    equipment: Mapped["RentalEquipment"] = relationship(back_populates="availability_blocks")
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ck_rental_availability_valid_range"),
        Index("ix_rental_availability_equipment_range", "equipment_id", "starts_at", "ends_at"),
    )


class RentalRequest(Base):
    __tablename__ = "rental_requests"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    requester_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="CASCADE"), index=True
    )
    lessor_profile_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("rental_lessor_profiles.id", ondelete="RESTRICT"), index=True
    )
    equipment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("rental_equipment.id", ondelete="RESTRICT"), index=True
    )
    pricing_rule_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("rental_pricing_rules.id", ondelete="RESTRICT"), index=True
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    requested_units: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    operator_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(
        String(30), default=RentalRequestStatus.PENDING.value, index=True
    )
    price_per_unit_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    rental_amount_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    deposit_amount_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_amount_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(10), default="TOMAN")
    delivery_address: Mapped[str | None] = mapped_column(Text)
    requester_note: Mapped[str | None] = mapped_column(Text)
    lessor_note: Mapped[str | None] = mapped_column(Text)
    admin_note: Mapped[str | None] = mapped_column(Text)
    cancel_reason: Mapped[str | None] = mapped_column(Text)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    lessor_profile: Mapped["LessorProfile"] = relationship(back_populates="requests")
    equipment: Mapped["RentalEquipment"] = relationship(back_populates="requests")
    status_logs: Mapped[list["RentalRequestStatusLog"]] = relationship(
        back_populates="request", cascade="all, delete-orphan"
    )
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ck_rental_request_valid_range"),
        CheckConstraint("requested_units > 0", name="ck_rental_request_units_positive"),
        CheckConstraint(
            "price_per_unit_snapshot IS NULL OR price_per_unit_snapshot >= 0",
            name="ck_rental_request_unit_price_nonnegative",
        ),
        CheckConstraint(
            "total_amount_snapshot IS NULL OR total_amount_snapshot >= 0",
            name="ck_rental_request_total_nonnegative",
        ),
        Index(
            "ix_rental_requests_equipment_range_status",
            "equipment_id",
            "starts_at",
            "ends_at",
            "status",
        ),
        Index("ix_rental_requests_requester_status", "requester_user_id", "status"),
        Index("ix_rental_requests_lessor_status", "lessor_profile_id", "status"),
    )


class RentalRequestStatusLog(Base):
    __tablename__ = "rental_request_status_logs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("rental_requests.id", ondelete="CASCADE"), index=True
    )
    changed_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="SET NULL"), index=True
    )
    from_status: Mapped[str | None] = mapped_column(String(30))
    to_status: Mapped[str] = mapped_column(String(30), index=True)
    note: Mapped[str | None] = mapped_column(Text)
    event_key: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    request: Mapped["RentalRequest"] = relationship(back_populates="status_logs")
    __table_args__ = (Index("ix_rental_request_logs_request_created", "request_id", "created_at"),)
