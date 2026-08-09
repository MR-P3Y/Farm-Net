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
from app.modules.services.enums import (
    ServiceContactMethod,
    ServiceOfferStatus,
    ServicePricingType,
    ServiceProviderStatus,
    ServiceRequestStatus,
)


class ServiceCategory(Base):
    __tablename__ = "service_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("service_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    sort_order: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    parent: Mapped["ServiceCategory | None"] = relationship(
        remote_side="ServiceCategory.id",
        back_populates="children",
    )
    children: Mapped[list["ServiceCategory"]] = relationship(back_populates="parent")

    provider_links: Mapped[list["ServiceProviderCategory"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )
    offers: Mapped[list["ServiceOffer"]] = relationship(back_populates="category")
    requests: Mapped[list["ServiceRequest"]] = relationship(back_populates="category")

    __table_args__ = (
        Index("ix_service_categories_parent_active", "parent_id", "is_active"),
        Index("ix_service_categories_active_sort", "is_active", "sort_order"),
    )


class ServiceProviderProfile(Base):
    __tablename__ = "service_provider_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    display_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    title: Mapped[str | None] = mapped_column(String(180), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_years: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    province_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    city_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    village_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)

    province_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    village_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    service_area: Mapped[str | None] = mapped_column(String(255), nullable=True)

    avatar_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_media_file_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("media_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default=ServiceProviderStatus.DRAFT.value,
        nullable=False,
        index=True,
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    rating_average: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0, nullable=False)
    reviews_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    requests_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    completed_requests_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    accepting_requests: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    availability_status: Mapped[str] = mapped_column(
        String(30), default="available", nullable=False
    )
    typical_response_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
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

    category_links: Mapped[list["ServiceProviderCategory"]] = relationship(
        back_populates="provider_profile",
        cascade="all, delete-orphan",
    )
    offers: Mapped[list["ServiceOffer"]] = relationship(back_populates="provider_profile")
    requests: Mapped[list["ServiceRequest"]] = relationship(back_populates="provider_profile")

    __table_args__ = (
        Index("ix_service_provider_profiles_geo", "province_id", "city_id", "village_id"),
        Index("ix_service_provider_profiles_status_featured", "status", "is_featured"),
        Index("ix_service_provider_profiles_rating", "rating_average", "reviews_count"),
    )


class ServiceProviderCategory(Base):
    __tablename__ = "service_provider_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    provider_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("service_provider_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("service_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    provider_profile: Mapped["ServiceProviderProfile"] = relationship(
        back_populates="category_links",
    )
    category: Mapped["ServiceCategory"] = relationship(back_populates="provider_links")

    __table_args__ = (
        UniqueConstraint(
            "provider_profile_id",
            "category_id",
            name="uq_service_provider_categories_provider_category",
        ),
    )


class ServiceOffer(Base):
    __tablename__ = "service_offers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    provider_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("service_provider_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("service_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(220), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    short_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String(50),
        default=ServiceOfferStatus.DRAFT.value,
        nullable=False,
        index=True,
    )
    pricing_type: Mapped[str] = mapped_column(
        String(40),
        default=ServicePricingType.NEGOTIABLE.value,
        nullable=False,
        index=True,
    )
    price_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="TOMAN", nullable=False)

    province_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    city_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    village_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)

    province_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    village_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    service_area: Mapped[str | None] = mapped_column(String(255), nullable=True)

    latitude: Mapped[str | None] = mapped_column(String(40), nullable=True)
    longitude: Mapped[str | None] = mapped_column(String(40), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    views_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    requests_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    completed_requests_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
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

    provider_profile: Mapped["ServiceProviderProfile"] = relationship(back_populates="offers")
    category: Mapped["ServiceCategory | None"] = relationship(back_populates="offers")
    media: Mapped[list["ServiceOfferMedia"]] = relationship(
        back_populates="offer",
        cascade="all, delete-orphan",
    )
    requests: Mapped[list["ServiceRequest"]] = relationship(back_populates="offer")

    __table_args__ = (
        UniqueConstraint("provider_profile_id", "slug", name="uq_service_offers_provider_slug"),
        Index("ix_service_offers_provider_status", "provider_profile_id", "status"),
        Index("ix_service_offers_category_status", "category_id", "status"),
        Index("ix_service_offers_public_lookup", "status", "deleted_at", "is_active"),
        Index("ix_service_offers_geo", "province_id", "city_id", "village_id"),
        Index("ix_service_offers_price", "price_amount"),
    )


class ServiceOfferMedia(Base):
    __tablename__ = "service_offer_media"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    offer_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("service_offers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    media_file_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("media_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    alt_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    portfolio_stage: Mapped[str | None] = mapped_column(String(20), nullable=True)

    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    offer: Mapped["ServiceOffer"] = relationship(back_populates="media")

    __table_args__ = (
        Index("ix_service_offer_media_offer_sort", "offer_id", "sort_order"),
        Index("ix_service_offer_media_offer_primary", "offer_id", "is_primary"),
    )


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    requester_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_profile_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("service_provider_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    offer_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("service_offers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("service_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    contact_method: Mapped[str] = mapped_column(
        String(40),
        default=ServiceContactMethod.IN_APP.value,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=ServiceRequestStatus.OPEN.value,
        nullable=False,
        index=True,
    )

    budget_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="TOMAN", nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    province_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    city_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    village_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)

    province_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    village_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    latitude: Mapped[str | None] = mapped_column(String(40), nullable=True)
    longitude: Mapped[str | None] = mapped_column(String(40), nullable=True)

    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    provider_profile: Mapped["ServiceProviderProfile | None"] = relationship(
        back_populates="requests",
    )
    offer: Mapped["ServiceOffer | None"] = relationship(back_populates="requests")
    category: Mapped["ServiceCategory | None"] = relationship(back_populates="requests")
    status_logs: Mapped[list["ServiceRequestStatusLog"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_service_requests_requester_status", "requester_user_id", "status"),
        Index("ix_service_requests_provider_status", "provider_profile_id", "status"),
        Index("ix_service_requests_offer_status", "offer_id", "status"),
        Index("ix_service_requests_category_status", "category_id", "status"),
        Index("ix_service_requests_created_status", "created_at", "status"),
    )


class ServiceRequestStatusLog(Base):
    __tablename__ = "service_request_status_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    request_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("service_requests.id", ondelete="CASCADE"),
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

    request: Mapped["ServiceRequest"] = relationship(back_populates="status_logs")

    __table_args__ = (Index("ix_service_request_logs_request_created", "request_id", "created_at"),)
