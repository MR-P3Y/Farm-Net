from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.farms.models import Farm, FarmPlot
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

    def add(self, row: Farm) -> Farm:
        self.db.add(row)
        self.db.flush()
        return row

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
