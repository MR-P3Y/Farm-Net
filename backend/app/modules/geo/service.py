from sqlalchemy.orm import Session

from app.modules.geo.repository import GeoRepository
from app.modules.geo.schemas import (
    GeoCityOut,
    GeoCountyOut,
    GeoDistrictOut,
    GeoProvinceOut,
    GeoRuralDistrictOut,
    GeoVillageOut,
)


class GeoService:
    def __init__(self, db: Session) -> None:
        self.repo = GeoRepository(db)

    def list_provinces(self) -> list[GeoProvinceOut]:
        return [
            GeoProvinceOut(
                id=item.id,
                name=item.name,
                amar_code=item.amar_code,
            )
            for item in self.repo.list_provinces()
        ]

    def list_counties(self, *, province_id: int | None = None) -> list[GeoCountyOut]:
        return [
            GeoCountyOut(
                id=item.id,
                province_id=item.province_id,
                name=item.name,
                amar_code=item.amar_code,
            )
            for item in self.repo.list_counties(province_id=province_id)
        ]

    def list_districts(
        self,
        *,
        province_id: int | None = None,
        county_id: int | None = None,
    ) -> list[GeoDistrictOut]:
        return [
            GeoDistrictOut(
                id=item.id,
                province_id=item.province_id,
                county_id=item.county_id,
                name=item.name,
                amar_code=item.amar_code,
            )
            for item in self.repo.list_districts(
                province_id=province_id,
                county_id=county_id,
            )
        ]

    def list_rural_districts(
        self,
        *,
        province_id: int | None = None,
        county_id: int | None = None,
        district_id: int | None = None,
    ) -> list[GeoRuralDistrictOut]:
        return [
            GeoRuralDistrictOut(
                id=item.id,
                province_id=item.province_id,
                county_id=item.county_id,
                district_id=item.district_id,
                name=item.name,
                amar_code=item.amar_code,
            )
            for item in self.repo.list_rural_districts(
                province_id=province_id,
                county_id=county_id,
                district_id=district_id,
            )
        ]

    def list_cities(
        self,
        *,
        province_id: int | None = None,
        county_id: int | None = None,
        district_id: int | None = None,
        q: str | None = None,
    ) -> list[GeoCityOut]:
        return [
            GeoCityOut(
                id=item.id,
                province_id=item.province_id,
                county_id=item.county_id,
                district_id=item.district_id,
                name=item.name,
                city_type=item.city_type,
                amar_code=item.amar_code,
            )
            for item in self.repo.list_cities(
                province_id=province_id,
                county_id=county_id,
                district_id=district_id,
                q=q,
            )
        ]

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
    ) -> tuple[list[GeoVillageOut], int]:
        items, total = self.repo.list_villages(
            page=page,
            page_size=page_size,
            province_id=province_id,
            county_id=county_id,
            district_id=district_id,
            rural_district_id=rural_district_id,
            q=q,
        )

        return [
            GeoVillageOut(
                id=item.id,
                province_id=item.province_id,
                county_id=item.county_id,
                district_id=item.district_id,
                rural_district_id=item.rural_district_id,
                name=item.name,
                village_type=item.village_type,
                diag=item.diag,
                amar_code=item.amar_code,
            )
            for item in items
        ], total
