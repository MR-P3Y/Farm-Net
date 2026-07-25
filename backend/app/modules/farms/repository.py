from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.farms.models import (
    Farm,
    FarmAuditLog,
    FarmCrop,
    FarmCropCategory,
    FarmCropCycle,
    FarmCropVariety,
    FarmIrrigationProfile,
    FarmLabObservation,
    FarmPlot,
    FarmSoilProfile,
    FarmWaterSource,
)
from app.modules.geo.models import (
    GeoCity,
    GeoCounty,
    GeoDistrict,
    GeoProvince,
    GeoRuralDistrict,
    GeoVillage,
)


class FarmRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, row):
        self.db.add(row)
        self.db.flush()
        return row

    def add_audit(
        self, *, farm_id: int, actor_user_id: int, action: str,
        target_type: str, target_id: int, details: dict | None = None,
    ) -> FarmAuditLog:
        return self.add(FarmAuditLog(
            farm_id=farm_id,
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
        ))

    def get_owned(
        self,
        *,
        farm_id: int,
        owner_user_id: int,
        for_update: bool = False,
    ) -> Farm | None:
        query = self.db.query(Farm).filter(
            Farm.id == farm_id,
            Farm.owner_user_id == owner_user_id,
        )
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def get_owned_for_update(self, *, farm_id: int, owner_user_id: int) -> Farm | None:
        return self.get_owned(
            farm_id=farm_id,
            owner_user_id=owner_user_id,
            for_update=True,
        )

    def list_owned(
        self,
        *,
        owner_user_id: int,
        include_archived: bool,
        offset: int,
        limit: int,
    ) -> tuple[list[Farm], int]:
        query = self.db.query(Farm).filter(Farm.owner_user_id == owner_user_id)
        if not include_archived:
            query = query.filter(Farm.status == "active")
        total = query.count()
        rows = (
            query.order_by(Farm.updated_at.desc(), Farm.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return rows, total

    def add_plot(self, row: FarmPlot) -> FarmPlot:
        self.db.add(row)
        self.db.flush()
        return row

    def get_owned_plot(
        self,
        *,
        farm_id: int,
        plot_id: int,
        owner_user_id: int,
        for_update: bool = False,
    ) -> FarmPlot | None:
        query = (
            self.db.query(FarmPlot)
            .join(Farm, Farm.id == FarmPlot.farm_id)
            .filter(
                FarmPlot.id == plot_id,
                FarmPlot.farm_id == farm_id,
                Farm.owner_user_id == owner_user_id,
            )
        )
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def list_owned_plots(
        self,
        *,
        farm_id: int,
        owner_user_id: int,
        include_archived: bool,
    ) -> list[FarmPlot]:
        query = (
            self.db.query(FarmPlot)
            .join(Farm, Farm.id == FarmPlot.farm_id)
            .filter(FarmPlot.farm_id == farm_id, Farm.owner_user_id == owner_user_id)
        )
        if not include_archived:
            query = query.filter(FarmPlot.status == "active")
        return query.order_by(FarmPlot.updated_at.desc(), FarmPlot.id.desc()).all()

    def total_plot_area(self, *, farm_id: int, exclude_plot_id: int | None = None) -> Decimal:
        query = self.db.query(func.coalesce(func.sum(FarmPlot.area_sqm), 0)).filter(
            FarmPlot.farm_id == farm_id
        )
        if exclude_plot_id is not None:
            query = query.filter(FarmPlot.id != exclude_plot_id)
        return Decimal(query.scalar() or 0)

    def get_geo(self, model, geo_id: int):
        return (
            self.db.query(model)
            .filter(model.id == geo_id, model.is_active.is_(True))
            .one_or_none()
        )

    def get_province(self, geo_id: int) -> GeoProvince | None:
        return self.get_geo(GeoProvince, geo_id)

    def get_county(self, geo_id: int) -> GeoCounty | None:
        return self.get_geo(GeoCounty, geo_id)

    def get_district(self, geo_id: int) -> GeoDistrict | None:
        return self.get_geo(GeoDistrict, geo_id)

    def get_rural_district(self, geo_id: int) -> GeoRuralDistrict | None:
        return self.get_geo(GeoRuralDistrict, geo_id)

    def get_city(self, geo_id: int) -> GeoCity | None:
        return self.get_geo(GeoCity, geo_id)

    def get_village(self, geo_id: int) -> GeoVillage | None:
        return self.get_geo(GeoVillage, geo_id)

    def list_crop_categories(self) -> list[FarmCropCategory]:
        return (
            self.db.query(FarmCropCategory)
            .filter(FarmCropCategory.is_active.is_(True))
            .order_by(FarmCropCategory.sort_order, FarmCropCategory.id)
            .all()
        )

    def list_crops(self, category_id: int | None = None) -> list[FarmCrop]:
        query = self.db.query(FarmCrop).filter(FarmCrop.is_active.is_(True))
        if category_id is not None:
            query = query.filter(FarmCrop.category_id == category_id)
        return query.order_by(FarmCrop.sort_order, FarmCrop.id).all()

    def get_crop(self, crop_id: int) -> FarmCrop | None:
        return (
            self.db.query(FarmCrop)
            .filter(FarmCrop.id == crop_id, FarmCrop.is_active.is_(True))
            .one_or_none()
        )

    def list_varieties(self, crop_id: int) -> list[FarmCropVariety]:
        return (
            self.db.query(FarmCropVariety)
            .filter(
                FarmCropVariety.crop_id == crop_id,
                FarmCropVariety.is_active.is_(True),
            )
            .order_by(FarmCropVariety.sort_order, FarmCropVariety.id)
            .all()
        )

    def get_variety(self, variety_id: int) -> FarmCropVariety | None:
        return (
            self.db.query(FarmCropVariety)
            .filter(
                FarmCropVariety.id == variety_id,
                FarmCropVariety.is_active.is_(True),
            )
            .one_or_none()
        )

    def add_cycle(self, row: FarmCropCycle) -> FarmCropCycle:
        self.db.add(row)
        self.db.flush()
        return row

    def get_owned_cycle(
        self,
        *,
        farm_id: int,
        plot_id: int,
        cycle_id: int,
        owner_user_id: int,
        for_update: bool = False,
    ) -> FarmCropCycle | None:
        query = (
            self.db.query(FarmCropCycle)
            .join(FarmPlot, FarmPlot.id == FarmCropCycle.plot_id)
            .join(Farm, Farm.id == FarmPlot.farm_id)
            .filter(
                FarmCropCycle.id == cycle_id,
                FarmCropCycle.plot_id == plot_id,
                FarmPlot.farm_id == farm_id,
                Farm.owner_user_id == owner_user_id,
            )
        )
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def list_owned_cycles(
        self, *, farm_id: int, plot_id: int, owner_user_id: int
    ) -> list[FarmCropCycle]:
        return (
            self.db.query(FarmCropCycle)
            .join(FarmPlot, FarmPlot.id == FarmCropCycle.plot_id)
            .join(Farm, Farm.id == FarmPlot.farm_id)
            .filter(
                FarmCropCycle.plot_id == plot_id,
                FarmPlot.farm_id == farm_id,
                Farm.owner_user_id == owner_user_id,
            )
            .order_by(FarmCropCycle.planned_start_date.desc(), FarmCropCycle.id.desc())
            .all()
        )

    def overlapping_cycles(
        self,
        *,
        plot_id: int,
        starts_on,
        ends_on,
        exclude_cycle_id: int | None = None,
    ) -> list[FarmCropCycle]:
        query = self.db.query(FarmCropCycle).filter(
            FarmCropCycle.plot_id == plot_id,
            FarmCropCycle.status.in_(("planned", "active")),
            FarmCropCycle.planned_start_date <= ends_on,
            FarmCropCycle.planned_end_date >= starts_on,
        )
        if exclude_cycle_id is not None:
            query = query.filter(FarmCropCycle.id != exclude_cycle_id)
        return query.with_for_update().all()

    def get_soil_profile(self, plot_id: int) -> FarmSoilProfile | None:
        return self.db.query(FarmSoilProfile).filter(FarmSoilProfile.plot_id == plot_id).one_or_none()

    def get_irrigation_profile(self, plot_id: int) -> FarmIrrigationProfile | None:
        return self.db.query(FarmIrrigationProfile).filter(FarmIrrigationProfile.plot_id == plot_id).one_or_none()

    def list_water_sources(self, farm_id: int) -> list[FarmWaterSource]:
        return self.db.query(FarmWaterSource).filter(FarmWaterSource.farm_id == farm_id).order_by(FarmWaterSource.id.desc()).all()

    def get_water_source(self, *, farm_id: int, source_id: int, for_update: bool = False) -> FarmWaterSource | None:
        query = self.db.query(FarmWaterSource).filter(
            FarmWaterSource.id == source_id, FarmWaterSource.farm_id == farm_id
        )
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def list_lab_observations(
        self, *, soil_profile_id: int | None, water_source_id: int | None
    ) -> list[FarmLabObservation]:
        query = self.db.query(FarmLabObservation)
        if soil_profile_id is not None:
            query = query.filter(FarmLabObservation.soil_profile_id == soil_profile_id)
        else:
            query = query.filter(FarmLabObservation.water_source_id == water_source_id)
        return query.order_by(FarmLabObservation.sampled_on.desc(), FarmLabObservation.id.desc()).all()
