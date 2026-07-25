from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Date,
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
from app.modules.farms.enums import CropCycleStatus, CultivationMode, FarmStatus


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    declared_area_sqm: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default=FarmStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    archive_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    plots: Mapped[list["FarmPlot"]] = relationship(back_populates="farm")

    __table_args__ = (
        CheckConstraint(
            "declared_area_sqm IS NULL OR declared_area_sqm > 0",
            name="ck_farms_declared_area_positive",
        ),
        CheckConstraint(
            "(status = 'active' AND archived_at IS NULL AND archive_reason IS NULL) OR "
            "(status = 'archived' AND archived_at IS NOT NULL)",
            name="ck_farms_archive_state",
        ),
        CheckConstraint(
            "status in ('active', 'archived')",
            name="ck_farms_status",
        ),
        Index("ix_farms_owner_status_updated", "owner_user_id", "status", "updated_at"),
    )


class FarmPlot(Base):
    __tablename__ = "farm_plots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("farms.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    area_sqm: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    province_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("geo_provinces.id", ondelete="RESTRICT"), nullable=True
    )
    county_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("geo_counties.id", ondelete="RESTRICT"), nullable=True
    )
    district_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("geo_districts.id", ondelete="RESTRICT"), nullable=True
    )
    rural_district_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("geo_rural_districts.id", ondelete="RESTRICT"),
        nullable=True,
    )
    city_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("geo_cities.id", ondelete="RESTRICT"), nullable=True
    )
    village_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("geo_villages.id", ondelete="RESTRICT"), nullable=True
    )
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    boundary: Mapped[list | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), default=FarmStatus.ACTIVE.value, nullable=False
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    archive_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    farm: Mapped["Farm"] = relationship(back_populates="plots")
    crop_cycles: Mapped[list["FarmCropCycle"]] = relationship(back_populates="plot")

    __table_args__ = (
        CheckConstraint("area_sqm > 0", name="ck_farm_plots_area_positive"),
        CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="ck_farm_plots_coordinate_pair",
        ),
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="ck_farm_plots_latitude",
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="ck_farm_plots_longitude",
        ),
        CheckConstraint(
            "(status = 'active' AND archived_at IS NULL AND archive_reason IS NULL) OR "
            "(status = 'archived' AND archived_at IS NOT NULL)",
            name="ck_farm_plots_archive_state",
        ),
        CheckConstraint(
            "status in ('active', 'archived')",
            name="ck_farm_plots_status",
        ),
        Index("ix_farm_plots_farm_status_updated", "farm_id", "status", "updated_at"),
        Index(
            "ix_farm_plots_geo",
            "province_id",
            "county_id",
            "district_id",
            "rural_district_id",
            "city_id",
            "village_id",
        ),
    )


class FarmCropCycle(Base):
    __tablename__ = "farm_crop_cycles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    plot_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("farm_plots.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    crop_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("farm_crops.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    variety_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("farm_crop_varieties.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    title: Mapped[str | None] = mapped_column(String(180), nullable=True)
    cultivation_mode: Mapped[str] = mapped_column(
        String(30), default=CultivationMode.SINGLE.value, nullable=False
    )
    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), default=CropCycleStatus.PLANNED.value, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    plot: Mapped["FarmPlot"] = relationship(back_populates="crop_cycles")
    crop: Mapped["FarmCrop"] = relationship()
    variety: Mapped["FarmCropVariety | None"] = relationship()

    __table_args__ = (
        CheckConstraint(
            "planned_end_date >= planned_start_date",
            name="ck_farm_crop_cycles_planned_dates",
        ),
        CheckConstraint(
            "actual_end_date IS NULL OR actual_start_date IS NOT NULL",
            name="ck_farm_crop_cycles_actual_end_requires_start",
        ),
        CheckConstraint(
            "actual_end_date IS NULL OR actual_end_date >= actual_start_date",
            name="ck_farm_crop_cycles_actual_dates",
        ),
        CheckConstraint(
            "cultivation_mode in ('single', 'intercrop')",
            name="ck_farm_crop_cycles_cultivation_mode",
        ),
        CheckConstraint(
            "status in ('planned', 'active', 'completed', 'cancelled')",
            name="ck_farm_crop_cycles_status",
        ),
        CheckConstraint(
            "(status = 'planned' AND actual_start_date IS NULL AND actual_end_date IS NULL) OR "
            "(status = 'active' AND actual_start_date IS NOT NULL AND actual_end_date IS NULL) OR "
            "(status = 'completed' AND actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL) OR "
            "(status = 'cancelled' AND actual_end_date IS NULL)",
            name="ck_farm_crop_cycles_lifecycle_dates",
        ),
        Index(
            "ix_farm_crop_cycles_plot_status_dates",
            "plot_id",
            "status",
            "planned_start_date",
            "planned_end_date",
        ),
    )


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
