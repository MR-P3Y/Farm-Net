from pydantic import BaseModel


class GeoProvinceOut(BaseModel):
    id: int
    name: str
    amar_code: str


class GeoCountyOut(BaseModel):
    id: int
    province_id: int
    name: str
    amar_code: str


class GeoDistrictOut(BaseModel):
    id: int
    province_id: int
    county_id: int
    name: str
    amar_code: str


class GeoRuralDistrictOut(BaseModel):
    id: int
    province_id: int
    county_id: int
    district_id: int
    name: str
    amar_code: str


class GeoCityOut(BaseModel):
    id: int
    province_id: int
    county_id: int
    district_id: int | None = None
    name: str
    city_type: str | None = None
    amar_code: str


class GeoVillageOut(BaseModel):
    id: int
    province_id: int
    county_id: int
    district_id: int | None = None
    rural_district_id: int | None = None
    name: str
    village_type: str | None = None
    diag: str | None = None
    amar_code: str


class GeoPlaceOut(BaseModel):
    reference: str
    display_name: str
    short_name: str
    latitude: str
    longitude: str
    category: str | None = None
    place_type: str | None = None
    country_code: str | None = None
    province_id: int | None = None
    county_id: int | None = None
    district_id: int | None = None
    rural_district_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None
    provider: str
    attribution: str


class GeoPlaceSearchResponse(BaseModel):
    success: bool
    data: list[GeoPlaceOut]
    message: str
    meta: dict


class GeoPlaceReverseResponse(BaseModel):
    success: bool
    data: GeoPlaceOut
    message: str
    meta: dict
