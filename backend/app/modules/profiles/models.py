from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.profiles.enums import (
    DocumentStatus,
    DocumentType,
    VerificationStatus,
    VerificationTargetRole,
)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(150), nullable=True)

    national_id: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
    )

    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    gender: Mapped[str | None] = mapped_column(
        String(30),
        default=None,
        nullable=True,
    )

    province_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("geo_provinces.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    county_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("geo_counties.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    district_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("geo_districts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rural_district_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("geo_rural_districts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    city_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("geo_cities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    village_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("geo_villages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    avatar_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_user_profiles_name", "first_name", "last_name"),
        Index(
            "ix_user_profiles_geo",
            "province_id",
            "county_id",
            "city_id",
            "village_id",
        ),
    )


class UserDocument(Base):
    __tablename__ = "user_documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    document_type: Mapped[str] = mapped_column(
        String(80),
        default=DocumentType.OTHER.value,
        nullable=False,
        index=True,
    )

    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(150), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    media_file_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("media_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default=DocumentStatus.PENDING.value,
        nullable=False,
        index=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reject_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    verification_links: Mapped[list["VerificationRequestDocument"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_user_documents_user_type_status",
            "user_id",
            "document_type",
            "status",
        ),
    )


class VerificationRequest(Base):
    __tablename__ = "verification_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_role: Mapped[str] = mapped_column(
        String(80),
        default=VerificationTargetRole.SHOP_OWNER.value,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default=VerificationStatus.DRAFT.value,
        nullable=False,
        index=True,
    )

    request_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    documents: Mapped[list["VerificationRequestDocument"]] = relationship(
        back_populates="verification_request",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["VerificationReview"]] = relationship(
        back_populates="verification_request",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_verification_requests_user_role_status",
            "user_id",
            "target_role",
            "status",
        ),
        Index("ix_verification_requests_status_created", "status", "created_at"),
    )


class VerificationRequestDocument(Base):
    __tablename__ = "verification_request_documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    verification_request_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("verification_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    verification_request: Mapped["VerificationRequest"] = relationship(
        back_populates="documents",
    )
    document: Mapped["UserDocument"] = relationship(
        back_populates="verification_links",
    )

    __table_args__ = (
        UniqueConstraint(
            "verification_request_id",
            "document_id",
            name="uq_verification_request_documents_request_document",
        ),
    )


class VerificationReview(Base):
    __tablename__ = "verification_reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    verification_request_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("verification_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reviewer_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    verification_request: Mapped["VerificationRequest"] = relationship(
        back_populates="reviews",
    )

    __table_args__ = (
        Index(
            "ix_verification_reviews_request_action",
            "verification_request_id",
            "action",
        ),
    )
