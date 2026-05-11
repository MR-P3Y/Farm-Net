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
