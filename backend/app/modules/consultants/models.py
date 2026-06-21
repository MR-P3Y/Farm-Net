from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.media import models as media_models  # noqa: F401


class ConsultSpecialty(Base):
    __tablename__ = "consult_specialties"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(BigInteger, nullable=False, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    profile_links: Mapped[list["ConsultProfileSpecialty"]] = relationship(
        back_populates="specialty",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_consult_specialties_active_sort", "is_active", "sort_order"),
    )


class ConsultProfile(Base):
    __tablename__ = "consult_profiles"

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
    province_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    avatar_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_media_file_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("media_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        index=True,
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    rating_average: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    reviews_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    requests_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    completed_requests_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

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

    specialty_links: Mapped[list["ConsultProfileSpecialty"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )
    requests: Mapped[list["ConsultRequest"]] = relationship(
        back_populates="consultant_profile",
    )

    __table_args__ = (
        Index("ix_consult_profiles_status_featured", "status", "is_featured"),
        Index("ix_consult_profiles_geo", "province_id", "city_id"),
        Index("ix_consult_profiles_rating", "rating_average", "reviews_count"),
    )


class ConsultProfileSpecialty(Base):
    __tablename__ = "consult_profile_specialties"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("consult_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    specialty_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("consult_specialties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    profile: Mapped["ConsultProfile"] = relationship(back_populates="specialty_links")
    specialty: Mapped["ConsultSpecialty"] = relationship(back_populates="profile_links")

    __table_args__ = (
        UniqueConstraint(
            "profile_id",
            "specialty_id",
            name="uq_consult_profile_specialties_profile_specialty",
        ),
    )


class ConsultRequest(Base):
    __tablename__ = "consult_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    requester_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consultant_profile_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("consult_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    specialty_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("consult_specialties.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    contact_method: Mapped[str] = mapped_column(String(40), nullable=False, default="in_app")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open", index=True)

    budget_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="IRR")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    consultant_note: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    consultant_profile: Mapped[ConsultProfile | None] = relationship(
        back_populates="requests",
    )
    specialty: Mapped[ConsultSpecialty | None] = relationship()
    status_logs: Mapped[list["ConsultRequestStatusLog"]] = relationship(
        back_populates="consult_request",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_consult_requests_requester_status", "requester_user_id", "status"),
        Index("ix_consult_requests_consultant_status", "consultant_profile_id", "status"),
        Index("ix_consult_requests_specialty_status", "specialty_id", "status"),
        Index("ix_consult_requests_created_status", "created_at", "status"),
    )


class ConsultRequestStatusLog(Base):
    __tablename__ = "consult_request_status_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    request_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("consult_requests.id", ondelete="CASCADE"),
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

    consult_request: Mapped["ConsultRequest"] = relationship(back_populates="status_logs")

    __table_args__ = (
        Index("ix_consult_request_logs_request_created", "request_id", "created_at"),
    )
