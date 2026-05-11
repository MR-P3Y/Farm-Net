from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GeoProvince(Base):
    __tablename__ = "geo_provinces"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    amar_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

    counties: Mapped[list["GeoCounty"]] = relationship(
        back_populates="province",
        cascade="all, delete-orphan",
    )
    districts: Mapped[list["GeoDistrict"]] = relationship(
        back_populates="province",
        cascade="all, delete-orphan",
    )
    rural_districts: Mapped[list["GeoRuralDistrict"]] = relationship(
        back_populates="province",
        cascade="all, delete-orphan",
    )
    cities: Mapped[list["GeoCity"]] = relationship(
        back_populates="province",
        cascade="all, delete-orphan",
    )
    villages: Mapped[list["GeoVillage"]] = relationship(
        back_populates="province",
        cascade="all, delete-orphan",
    )


class GeoCounty(Base):
    __tablename__ = "geo_counties"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    province_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("geo_provinces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    amar_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

    province: Mapped["GeoProvince"] = relationship(back_populates="counties")
    districts: Mapped[list["GeoDistrict"]] = relationship(
        back_populates="county",
        cascade="all, delete-orphan",
    )
    rural_districts: Mapped[list["GeoRuralDistrict"]] = relationship(
        back_populates="county",
        cascade="all, delete-orphan",
    )
    cities: Mapped[list["GeoCity"]] = relationship(
        back_populates="county",
        cascade="all, delete-orphan",
    )
    villages: Mapped[list["GeoVillage"]] = relationship(
        back_populates="county",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_geo_counties_province_name", "province_id", "name"),
    )


class GeoDistrict(Base):
    __tablename__ = "geo_districts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    province_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("geo_provinces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    county_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("geo_counties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    amar_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

    province: Mapped["GeoProvince"] = relationship(back_populates="districts")
    county: Mapped["GeoCounty"] = relationship(back_populates="districts")
    rural_districts: Mapped[list["GeoRuralDistrict"]] = relationship(
        back_populates="district",
        cascade="all, delete-orphan",
    )
    cities: Mapped[list["GeoCity"]] = relationship(
        back_populates="district",
        cascade="all, delete-orphan",
    )
    villages: Mapped[list["GeoVillage"]] = relationship(
        back_populates="district",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_geo_districts_county_name", "county_id", "name"),
    )


class GeoRuralDistrict(Base):
    __tablename__ = "geo_rural_districts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    province_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("geo_provinces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    county_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("geo_counties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    district_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("geo_districts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    amar_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

    province: Mapped["GeoProvince"] = relationship(back_populates="rural_districts")
    county: Mapped["GeoCounty"] = relationship(back_populates="rural_districts")
    district: Mapped["GeoDistrict"] = relationship(back_populates="rural_districts")
    villages: Mapped[list["GeoVillage"]] = relationship(
        back_populates="rural_district",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_geo_rural_districts_district_name", "district_id", "name"),
    )


class GeoCity(Base):
    __tablename__ = "geo_cities"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    province_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("geo_provinces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    county_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("geo_counties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    district_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("geo_districts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    city_type: Mapped[str | None] = mapped_column(String(80), nullable=True)

    amar_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

    province: Mapped["GeoProvince"] = relationship(back_populates="cities")
    county: Mapped["GeoCounty"] = relationship(back_populates="cities")
    district: Mapped["GeoDistrict"] = relationship(back_populates="cities")

    __table_args__ = (
        Index("ix_geo_cities_county_name", "county_id", "name"),
        Index("ix_geo_cities_province_name", "province_id", "name"),
    )


class GeoVillage(Base):
    __tablename__ = "geo_villages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    province_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("geo_provinces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    county_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("geo_counties.id", ondelete="CASCADE"),
        nullable=False,
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

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    village_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    diag: Mapped[str | None] = mapped_column(String(100), nullable=True)

    amar_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

    province: Mapped["GeoProvince"] = relationship(back_populates="villages")
    county: Mapped["GeoCounty"] = relationship(back_populates="villages")
    district: Mapped["GeoDistrict"] = relationship(back_populates="villages")
    rural_district: Mapped["GeoRuralDistrict"] = relationship(
        back_populates="villages",
    )

    __table_args__ = (
        Index("ix_geo_villages_rural_district_name", "rural_district_id", "name"),
        Index("ix_geo_villages_county_name", "county_id", "name"),
    )
