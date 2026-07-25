from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.modules.farms.enums import CropCycleStatus, CultivationMode, FarmStatus


def _normalize_required(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Value cannot be blank")
    return normalized


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip() or None


class FarmCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    declared_area_sqm: Decimal | None = Field(default=None, gt=0, max_digits=18, decimal_places=2)

    _name = field_validator("name")(_normalize_required)
    _description = field_validator("description")(_normalize_optional)


class FarmUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    declared_area_sqm: Decimal | None = Field(default=None, gt=0, max_digits=18, decimal_places=2)

    _name = field_validator("name")(_normalize_required)
    _description = field_validator("description")(_normalize_optional)

    @model_validator(mode="after")
    def require_explicit_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class FarmArchiveIn(BaseModel):
    reason: str | None = Field(default=None, max_length=500)

    _reason = field_validator("reason")(_normalize_optional)


class FarmOwnerOut(BaseModel):
    id: int
    name: str
    description: str | None
    declared_area_sqm: Decimal | None
    status: FarmStatus
    archived_at: datetime | None
    archive_reason: str | None
    can_edit: bool
    can_archive: bool
    can_restore: bool
    created_at: datetime
    updated_at: datetime


class FarmOwnerDetailResponse(BaseModel):
    success: bool
    data: FarmOwnerOut
    message: str
    meta: dict


class FarmOwnerListResponse(BaseModel):
    success: bool
    data: list[FarmOwnerOut]
    message: str
    meta: dict


class FarmGeoPoint(BaseModel):
    latitude: Decimal = Field(ge=-90, le=90, max_digits=10, decimal_places=7)
    longitude: Decimal = Field(ge=-180, le=180, max_digits=10, decimal_places=7)


class FarmPlotFields(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    area_sqm: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    province_id: int | None = Field(default=None, ge=1)
    county_id: int | None = Field(default=None, ge=1)
    district_id: int | None = Field(default=None, ge=1)
    rural_district_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    village_id: int | None = Field(default=None, ge=1)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90, decimal_places=7)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180, decimal_places=7)
    boundary: list[FarmGeoPoint] | None = Field(default=None, min_length=4, max_length=500)

    _name = field_validator("name")(_normalize_required)
    _description = field_validator("description")(_normalize_optional)

    @model_validator(mode="after")
    def validate_geometry(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be provided together")
        if self.boundary is not None:
            first = self.boundary[0]
            last = self.boundary[-1]
            if first != last:
                raise ValueError("boundary must be a closed ring")
            if len({(point.latitude, point.longitude) for point in self.boundary[:-1]}) < 3:
                raise ValueError("boundary must contain at least three distinct points")
        return self


class FarmPlotCreateIn(FarmPlotFields):
    pass


class FarmPlotUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    area_sqm: Decimal | None = Field(default=None, gt=0, max_digits=18, decimal_places=2)
    province_id: int | None = Field(default=None, ge=1)
    county_id: int | None = Field(default=None, ge=1)
    district_id: int | None = Field(default=None, ge=1)
    rural_district_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    village_id: int | None = Field(default=None, ge=1)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90, decimal_places=7)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180, decimal_places=7)
    boundary: list[FarmGeoPoint] | None = Field(default=None, min_length=4, max_length=500)

    _name = field_validator("name")(_normalize_required)
    _description = field_validator("description")(_normalize_optional)

    @model_validator(mode="after")
    def require_field_and_validate_boundary(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        if self.boundary is not None:
            first, last = self.boundary[0], self.boundary[-1]
            if first != last:
                raise ValueError("boundary must be a closed ring")
            if len({(point.latitude, point.longitude) for point in self.boundary[:-1]}) < 3:
                raise ValueError("boundary must contain at least three distinct points")
        return self


class FarmPlotOut(BaseModel):
    id: int
    farm_id: int
    name: str
    description: str | None
    area_sqm: Decimal
    province_id: int | None
    county_id: int | None
    district_id: int | None
    rural_district_id: int | None
    city_id: int | None
    village_id: int | None
    latitude: Decimal | None
    longitude: Decimal | None
    boundary: list[FarmGeoPoint] | None
    status: FarmStatus
    archived_at: datetime | None
    archive_reason: str | None
    created_at: datetime
    updated_at: datetime


class FarmPlotDetailResponse(BaseModel):
    success: bool
    data: FarmPlotOut
    message: str
    meta: dict


class FarmPlotListResponse(BaseModel):
    success: bool
    data: list[FarmPlotOut]
    message: str
    meta: dict


class CropCategoryOut(BaseModel):
    id: int
    code: str
    title: str
    description: str | None


class CropOut(BaseModel):
    id: int
    category_id: int
    code: str
    title: str
    scientific_name: str | None
    default_cycle_type: str


class CropVarietyOut(BaseModel):
    id: int
    crop_id: int
    code: str
    title: str
    scientific_name: str | None


class FarmCropCycleCreateIn(BaseModel):
    crop_id: int = Field(ge=1)
    variety_id: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, max_length=180)
    cultivation_mode: CultivationMode = CultivationMode.SINGLE
    planned_start_date: date
    planned_end_date: date
    notes: str | None = Field(default=None, max_length=5000)

    _title = field_validator("title")(_normalize_optional)
    _notes = field_validator("notes")(_normalize_optional)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.planned_end_date < self.planned_start_date:
            raise ValueError("planned_end_date cannot be before planned_start_date")
        return self


class FarmCropCycleUpdateIn(BaseModel):
    crop_id: int | None = Field(default=None, ge=1)
    variety_id: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, max_length=180)
    cultivation_mode: CultivationMode | None = None
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    notes: str | None = Field(default=None, max_length=5000)

    _title = field_validator("title")(_normalize_optional)
    _notes = field_validator("notes")(_normalize_optional)

    @model_validator(mode="after")
    def require_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class FarmCropCycleOut(BaseModel):
    id: int
    plot_id: int
    crop_id: int
    variety_id: int | None
    title: str | None
    cultivation_mode: CultivationMode
    planned_start_date: date
    planned_end_date: date
    actual_start_date: date | None
    actual_end_date: date | None
    status: CropCycleStatus
    notes: str | None
    can_edit: bool
    can_start: bool
    can_complete: bool
    can_cancel: bool
    created_at: datetime
    updated_at: datetime


class FarmCropCycleDetailResponse(BaseModel):
    success: bool
    data: FarmCropCycleOut
    message: str
    meta: dict


class FarmCropCycleListResponse(BaseModel):
    success: bool
    data: list[FarmCropCycleOut]
    message: str
    meta: dict


class FarmCropCycleTransitionIn(BaseModel):
    effective_date: date
