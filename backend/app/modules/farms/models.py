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
    event,
    inspect,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.farms.enums import (
    CropCycleStatus,
    CultivationMode,
    FarmStatus,
    IrrigationMethod,
    SoilTexture,
    WaterSourceType,
)


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


class FarmOperation(Base):
    __tablename__ = "farm_operations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cycle_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("farm_crop_cycles.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    occurred_on: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    __table_args__ = (
        CheckConstraint(
            "operation_type in "
            "('land_preparation','planting','irrigation','fertilizing','spraying',"
            "'weeding','pruning','monitoring','other')",
            name="ck_farm_operations_type",
        ),
        Index("ix_farm_operations_cycle_occurred", "cycle_id", "occurred_on"),
    )


class FarmOperationInput(Base):
    __tablename__ = "farm_operation_inputs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    operation_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("farm_operations.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    measurement_unit_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("farm_measurement_units.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_farm_operation_inputs_quantity_positive"),
    )


class FarmHarvestObservation(Base):
    __tablename__ = "farm_harvest_observations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cycle_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("farm_crop_cycles.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    harvested_on: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    measurement_unit_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("farm_measurement_units.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    quality_grade: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_farm_harvest_quantity_positive"),
        Index("ix_farm_harvest_cycle_date", "cycle_id", "harvested_on"),
    )


class FarmRecordMedia(Base):
    __tablename__ = "farm_record_media"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cycle_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("farm_crop_cycles.id", ondelete="RESTRICT"),
        nullable=True, index=True
    )
    operation_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("farm_operations.id", ondelete="RESTRICT"),
        nullable=True, index=True
    )
    harvest_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("farm_harvest_observations.id", ondelete="RESTRICT"),
        nullable=True, index=True
    )
    media_file_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("media_files.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    caption: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        CheckConstraint(
            "(cycle_id IS NOT NULL) + (operation_id IS NOT NULL) + "
            "(harvest_id IS NOT NULL) = 1",
            name="ck_farm_record_media_exact_subject",
        ),
        UniqueConstraint("cycle_id", "media_file_id", name="uq_farm_record_media_cycle_file"),
        UniqueConstraint("operation_id", "media_file_id", name="uq_farm_record_media_operation_file"),
        UniqueConstraint("harvest_id", "media_file_id", name="uq_farm_record_media_harvest_file"),
    )


class FarmAuditLog(Base):
    __tablename__ = "farm_audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("farms.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    actor_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        Index("ix_farm_audit_logs_farm_created", "farm_id", "created_at"),
        Index("ix_farm_audit_logs_target", "target_type", "target_id"),
    )


class FarmSoilProfile(Base):
    __tablename__ = "farm_soil_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    plot_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("farm_plots.id", ondelete="RESTRICT"),
        nullable=False, unique=True, index=True
    )
    texture: Mapped[str] = mapped_column(
        String(30), default=SoilTexture.UNKNOWN.value, nullable=False
    )
    depth_cm: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    drainage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    __table_args__ = (
        CheckConstraint(
            "texture in ('sandy','loamy','clay','silty','mixed','unknown')",
            name="ck_farm_soil_profiles_texture",
        ),
        CheckConstraint("depth_cm IS NULL OR depth_cm > 0", name="ck_farm_soil_profiles_depth_positive"),
    )


class FarmWaterSource(Base):
    __tablename__ = "farm_water_sources"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("farms.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(30), default=WaterSourceType.OTHER.value, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default=FarmStatus.ACTIVE.value, nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    __table_args__ = (
        CheckConstraint(
            "source_type in ('well','spring','river','canal','reservoir','municipal','other')",
            name="ck_farm_water_sources_type",
        ),
        CheckConstraint(
            "(status = 'active' AND archived_at IS NULL) OR "
            "(status = 'archived' AND archived_at IS NOT NULL)",
            name="ck_farm_water_sources_archive_state",
        ),
        Index("ix_farm_water_sources_farm_status", "farm_id", "status"),
    )


class FarmIrrigationProfile(Base):
    __tablename__ = "farm_irrigation_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    plot_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("farm_plots.id", ondelete="RESTRICT"),
        nullable=False, unique=True, index=True
    )
    water_source_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("farm_water_sources.id", ondelete="RESTRICT"),
        nullable=True, index=True
    )
    method: Mapped[str] = mapped_column(
        String(30), default=IrrigationMethod.OTHER.value, nullable=False
    )
    efficiency_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    __table_args__ = (
        CheckConstraint(
            "method in ('surface','drip','sprinkler','subsurface','rainfed','other')",
            name="ck_farm_irrigation_profiles_method",
        ),
        CheckConstraint(
            "efficiency_percent IS NULL OR (efficiency_percent >= 0 AND efficiency_percent <= 100)",
            name="ck_farm_irrigation_profiles_efficiency",
        ),
    )


class FarmLabObservation(Base):
    __tablename__ = "farm_lab_observations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    soil_profile_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("farm_soil_profiles.id", ondelete="RESTRICT"),
        nullable=True, index=True
    )
    water_source_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("farm_water_sources.id", ondelete="RESTRICT"),
        nullable=True, index=True
    )
    metric_code: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    unit_code: Mapped[str] = mapped_column(String(30), nullable=False)
    sampled_on: Mapped[date] = mapped_column(Date, nullable=False)
    tested_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    laboratory_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    __table_args__ = (
        CheckConstraint(
            "(soil_profile_id IS NOT NULL AND water_source_id IS NULL) OR "
            "(soil_profile_id IS NULL AND water_source_id IS NOT NULL)",
            name="ck_farm_lab_observations_exact_subject",
        ),
        CheckConstraint("value >= 0", name="ck_farm_lab_observations_value_nonnegative"),
        CheckConstraint("tested_on IS NULL OR tested_on >= sampled_on", name="ck_farm_lab_observations_dates"),
        Index("ix_farm_lab_observations_soil_sampled", "soil_profile_id", "sampled_on"),
        Index("ix_farm_lab_observations_water_sampled", "water_source_id", "sampled_on"),
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


def _reject_retained_farm_record_mutation(_mapper, _connection, target) -> None:
    raise RuntimeError(f"Retained farm record {target.__class__.__name__} is immutable")


def _protect_closed_cycle_update(_mapper, _connection, target) -> None:
    state = inspect(target)
    status_history = state.attrs.status.history
    previous_status = status_history.deleted[0] if status_history.deleted else target.status
    if previous_status in (CropCycleStatus.COMPLETED.value, CropCycleStatus.CANCELLED.value):
        raise RuntimeError("Closed farm crop cycle history is immutable")


for _retained_model in (
    FarmOperation,
    FarmOperationInput,
    FarmHarvestObservation,
    FarmRecordMedia,
    FarmLabObservation,
    FarmAuditLog,
):
    event.listen(_retained_model, "before_update", _reject_retained_farm_record_mutation)
    event.listen(_retained_model, "before_delete", _reject_retained_farm_record_mutation)

event.listen(FarmCropCycle, "before_update", _protect_closed_cycle_update)
event.listen(FarmCropCycle, "before_delete", _reject_retained_farm_record_mutation)
