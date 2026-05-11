from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.modules.geo.models import (
    GeoCity,
    GeoCounty,
    GeoDistrict,
    GeoProvince,
    GeoRuralDistrict,
    GeoVillage,
)


class GeoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_provinces(self) -> list[GeoProvince]:
        return (
            self.db.query(GeoProvince)
            .filter(GeoProvince.is_active.is_(True))
            .order_by(GeoProvince.name.asc())
            .all()
        )

    def list_counties(self, *, province_id: int | None = None) -> list[GeoCounty]:
        query = self.db.query(GeoCounty).filter(GeoCounty.is_active.is_(True))

        if province_id is not None:
            query = query.filter(GeoCounty.province_id == province_id)

        return query.order_by(GeoCounty.name.asc()).all()

    def list_districts(
        self,
        *,
        province_id: int | None = None,
        county_id: int | None = None,
    ) -> list[GeoDistrict]:
        query = self.db.query(GeoDistrict).filter(GeoDistrict.is_active.is_(True))

        if province_id is not None:
            query = query.filter(GeoDistrict.province_id == province_id)

        if county_id is not None:
            query = query.filter(GeoDistrict.county_id == county_id)

        return query.order_by(GeoDistrict.name.asc()).all()

    def list_rural_districts(
        self,
        *,
        province_id: int | None = None,
        county_id: int | None = None,
        district_id: int | None = None,
    ) -> list[GeoRuralDistrict]:
        query = self.db.query(GeoRuralDistrict).filter(
            GeoRuralDistrict.is_active.is_(True)
        )

        if province_id is not None:
            query = query.filter(GeoRuralDistrict.province_id == province_id)

        if county_id is not None:
            query = query.filter(GeoRuralDistrict.county_id == county_id)

        if district_id is not None:
            query = query.filter(GeoRuralDistrict.district_id == district_id)

        return query.order_by(GeoRuralDistrict.name.asc()).all()

    def list_cities(
        self,
        *,
        province_id: int | None = None,
        county_id: int | None = None,
        district_id: int | None = None,
        q: str | None = None,
    ) -> list[GeoCity]:
        query = self.db.query(GeoCity).filter(GeoCity.is_active.is_(True))

        if province_id is not None:
            query = query.filter(GeoCity.province_id == province_id)

        if county_id is not None:
            query = query.filter(GeoCity.county_id == county_id)

        if district_id is not None:
            query = query.filter(GeoCity.district_id == district_id)

        if q and q.strip():
            like = f"%{q.strip()}%"
            query = query.filter(GeoCity.name.ilike(like))

        return query.order_by(GeoCity.name.asc()).all()

    def list_villages(
        self,
        *,
        page: int,
        page_size: int,
        province_id: int | None = None,
        county_id: int | None = None,
        district_id: int | None = None,
        rural_district_id: int | None = None,
        q: str | None = None,
    ) -> tuple[list[GeoVillage], int]:
        query = self.db.query(GeoVillage).filter(GeoVillage.is_active.is_(True))

        if province_id is not None:
            query = query.filter(GeoVillage.province_id == province_id)

        if county_id is not None:
            query = query.filter(GeoVillage.county_id == county_id)

        if district_id is not None:
            query = query.filter(GeoVillage.district_id == district_id)

        if rural_district_id is not None:
            query = query.filter(GeoVillage.rural_district_id == rural_district_id)

        if q and q.strip():
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    GeoVillage.name.ilike(like),
                    GeoVillage.diag.ilike(like),
                )
            )

        total = query.count()

        items = (
            query.order_by(GeoVillage.name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total
