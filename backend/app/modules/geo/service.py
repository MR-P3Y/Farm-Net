from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.modules.geo.geocoding import GeocodingGateway, GeocodingPlace
from app.modules.geo.models import GeoCity, GeoCounty, GeoProvince, GeoVillage
from app.modules.geo.repository import GeoRepository
from app.modules.geo.schemas import (
    GeoCityOut,
    GeoCountyOut,
    GeoDistrictOut,
    GeoProvinceOut,
    GeoRuralDistrictOut,
    GeoVillageOut,
    GeoPlaceOut,
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


class GeoLocationSearchService:
    def __init__(self, db: Session, *, gateway: GeocodingGateway) -> None:
        self.repo = GeoRepository(db)
        self.gateway = gateway
        self.settings = get_settings()

    def search(
        self,
        *,
        query: str,
        language: str,
        limit: int,
    ) -> tuple[list[GeoPlaceOut], bool]:
        results, cached = self.gateway.search(
            query=" ".join(query.split()).strip(),
            language=language,
            limit=min(limit, self.settings.geocoding_max_results),
        )
        return [self._out(item) for item in results], cached

    def reverse(
        self,
        *,
        latitude: Decimal,
        longitude: Decimal,
        language: str,
    ) -> tuple[GeoPlaceOut, bool]:
        result, cached = self.gateway.reverse(
            latitude=latitude,
            longitude=longitude,
            language=language,
        )
        if result is None:
            raise AppException(
                "GEO_LOCATION_NOT_FOUND",
                "No readable location was found for this point",
                404,
            )
        return self._out(result), cached

    def _out(self, place: GeocodingPlace) -> GeoPlaceOut:
        hierarchy = self._resolve_hierarchy(place.address)
        return GeoPlaceOut(
            reference=place.reference,
            display_name=place.display_name,
            short_name=place.short_name,
            latitude=str(place.latitude),
            longitude=str(place.longitude),
            category=place.category,
            place_type=place.place_type,
            country_code=place.country_code,
            provider=place.provider,
            attribution=place.attribution,
            **hierarchy,
        )

    def _resolve_hierarchy(self, address: dict[str, str]) -> dict[str, int | None]:
        province = self.repo.find_unique_by_names(
            GeoProvince,
            names=_address_values(address, "state", "province"),
        )
        county = self.repo.find_unique_by_names(
            GeoCounty,
            names=_address_values(address, "county", "state_district"),
            province_id=province.id if province is not None else None,
        )
        village = self.repo.find_unique_by_names(
            GeoVillage,
            names=_address_values(address, "village", "hamlet"),
            province_id=province.id if province is not None else None,
            county_id=county.id if county is not None else None,
        )
        if village is not None:
            return {
                "province_id": village.province_id,
                "county_id": village.county_id,
                "district_id": village.district_id,
                "rural_district_id": village.rural_district_id,
                "city_id": None,
                "village_id": village.id,
            }
        city = self.repo.find_unique_by_names(
            GeoCity,
            names=_address_values(address, "city", "town", "municipality"),
            province_id=province.id if province is not None else None,
            county_id=county.id if county is not None else None,
        )
        if city is not None:
            return {
                "province_id": city.province_id,
                "county_id": city.county_id,
                "district_id": city.district_id,
                "rural_district_id": None,
                "city_id": city.id,
                "village_id": None,
            }
        return {
            "province_id": province.id if province is not None else None,
            "county_id": county.id if county is not None else None,
            "district_id": None,
            "rural_district_id": None,
            "city_id": None,
            "village_id": None,
        }


def _address_values(address: dict[str, str], *keys: str) -> list[str]:
    return [value for key in keys if (value := address.get(key))]
