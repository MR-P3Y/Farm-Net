from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
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
from app.modules.stores.enums import (
    StoreMemberRole,
    StoreMemberStatus,
    StoreStatus,
    StoreType,
)


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    owner_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        unique=True,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String(50),
        default=StoreStatus.DRAFT.value,
        nullable=False,
        index=True,
    )

    store_type: Mapped[str] = mapped_column(
        String(80),
        default=StoreType.OTHER.value,
        nullable=False,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

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

    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)

    logo_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    banner_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_media_file_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("media_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    banner_media_file_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("media_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    members: Mapped[list["StoreMember"]] = relationship(
        back_populates="store",
        cascade="all, delete-orphan",
    )
    status_history: Mapped[list["StoreStatusHistory"]] = relationship(
        back_populates="store",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_stores_owner_status", "owner_user_id", "status"),
        Index(
            "ix_stores_geo",
            "province_id",
            "county_id",
            "city_id",
            "village_id",
        ),
        Index("ix_stores_public_lookup", "status", "deleted_at", "slug"),
    )


class StoreMember(Base):
    __tablename__ = "store_members"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default=StoreMemberRole.STAFF.value,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=StoreMemberStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )

    invited_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    joined_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

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

    store: Mapped["Store"] = relationship(back_populates="members")

    __table_args__ = (
        UniqueConstraint("store_id", "user_id", name="uq_store_members_store_user"),
        Index("ix_store_members_user_status", "user_id", "status"),
    )


class StoreStatusHistory(Base):
    __tablename__ = "store_status_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="CASCADE"),
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

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    store: Mapped["Store"] = relationship(back_populates="status_history")

    __table_args__ = (
        Index("ix_store_status_history_store_created", "store_id", "created_at"),
    )
