from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.auth.models import AuthUser
from app.modules.farms.enums import (
    CropCycleStatus,
    CultivationMode,
    FarmStatus,
    LabSubjectType,
)
from app.modules.farms.models import (
    Farm,
    FarmCropCycle,
    FarmIrrigationProfile,
    FarmLabObservation,
    FarmSoilProfile,
    FarmWaterSource,
)
from app.modules.farms.repository import FarmRepository
from app.modules.farms.schemas import (
    FarmArchiveIn,
    CropCategoryOut,
    CropOut,
    CropVarietyOut,
    FarmCropCycleCreateIn,
    FarmCropCycleOut,
    FarmCropCycleUpdateIn,
    FarmCreateIn,
    FarmOwnerOut,
    FarmPlotCreateIn,
    FarmPlotOut,
    FarmPlotUpdateIn,
    IrrigationProfileIn,
    IrrigationProfileOut,
    LabObservationCreateIn,
    LabObservationOut,
    MeasurementUnitOut,
    SoilProfileIn,
    SoilProfileOut,
    WaterSourceIn,
    WaterSourceOut,
    FarmUpdateIn,
)


class FarmService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FarmRepository(db)

    def create(self, *, user: AuthUser, payload: FarmCreateIn) -> FarmOwnerOut:
        row = self.repo.add(
            Farm(
                owner_user_id=user.id,
                name=payload.name,
                description=payload.description,
                declared_area_sqm=payload.declared_area_sqm,
                status=FarmStatus.ACTIVE.value,
            )
        )
        self.repo.add_audit(
            farm_id=row.id, actor_user_id=user.id, action="farm.created",
            target_type="farm", target_id=row.id,
        )
        self.db.commit()
        self.db.refresh(row)
        return self._owner_out(row)

    def list_own(
        self,
        *,
        user: AuthUser,
        include_archived: bool,
        page: int,
        page_size: int,
    ) -> tuple[list[FarmOwnerOut], int]:
        rows, total = self.repo.list_owned(
            owner_user_id=user.id,
            include_archived=include_archived,
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        return [self._owner_out(row) for row in rows], total

    def get_own(self, *, user: AuthUser, farm_id: int) -> FarmOwnerOut:
        return self._owner_out(self._owned_or_404(user_id=user.id, farm_id=farm_id))

    def update(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        payload: FarmUpdateIn,
    ) -> FarmOwnerOut:
        row = self._owned_or_404(user_id=user.id, farm_id=farm_id, for_update=True)
        self._require_active(row)
        changes = payload.model_dump(exclude_unset=True)
        if "declared_area_sqm" in changes and changes["declared_area_sqm"] is not None:
            used_area = self.repo.total_plot_area(farm_id=row.id)
            if changes["declared_area_sqm"] < used_area:
                raise AppException(
                    code="FARM_AREA_BELOW_PLOTS",
                    message="Farm area cannot be smaller than total plot area",
                    status_code=409,
                    details={"used_area_sqm": str(used_area)},
                )
        for field, value in changes.items():
            setattr(row, field, value)
        self.repo.add_audit(
            farm_id=row.id, actor_user_id=user.id, action="farm.updated",
            target_type="farm", target_id=row.id,
            details={"fields": sorted(changes)},
        )
        self.db.commit()
        self.db.refresh(row)
        return self._owner_out(row)

    def archive(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        payload: FarmArchiveIn,
    ) -> FarmOwnerOut:
        row = self._owned_or_404(user_id=user.id, farm_id=farm_id, for_update=True)
        self._require_active(row)
        row.status = FarmStatus.ARCHIVED.value
        row.archived_at = datetime.now(UTC).replace(tzinfo=None)
        row.archive_reason = payload.reason
        self.repo.add_audit(
            farm_id=row.id, actor_user_id=user.id, action="farm.archived",
            target_type="farm", target_id=row.id,
        )
        self.db.commit()
        self.db.refresh(row)
        return self._owner_out(row)

    def restore(self, *, user: AuthUser, farm_id: int) -> FarmOwnerOut:
        row = self._owned_or_404(user_id=user.id, farm_id=farm_id, for_update=True)
        if row.status != FarmStatus.ARCHIVED.value:
            raise AppException(
                code="FARM_NOT_ARCHIVED",
                message="Farm is not archived",
                status_code=409,
            )
        row.status = FarmStatus.ACTIVE.value
        row.archived_at = None
        row.archive_reason = None
        self.repo.add_audit(
            farm_id=row.id, actor_user_id=user.id, action="farm.restored",
            target_type="farm", target_id=row.id,
        )
        self.db.commit()
        self.db.refresh(row)
        return self._owner_out(row)

    def _owned_or_404(
        self,
        *,
        user_id: int,
        farm_id: int,
        for_update: bool = False,
    ) -> Farm:
        row = self.repo.get_owned(
            farm_id=farm_id,
            owner_user_id=user_id,
            for_update=for_update,
        )
        if row is None:
            raise AppException(
                code="FARM_NOT_FOUND",
                message="Farm not found",
                status_code=404,
            )
        return row

    @staticmethod
    def _require_active(row: Farm) -> None:
        if row.status != FarmStatus.ACTIVE.value:
            raise AppException(
                code="FARM_ARCHIVED",
                message="Archived farm must be restored before editing",
                status_code=409,
            )

    @staticmethod
    def _owner_out(row: Farm) -> FarmOwnerOut:
        active = row.status == FarmStatus.ACTIVE.value
        return FarmOwnerOut(
            id=row.id,
            name=row.name,
            description=row.description,
            declared_area_sqm=row.declared_area_sqm,
            status=FarmStatus(row.status),
            archived_at=row.archived_at,
            archive_reason=row.archive_reason,
            can_edit=active,
            can_archive=active,
            can_restore=not active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class FarmPlotService:
    _geo_fields = (
        "province_id",
        "county_id",
        "district_id",
        "rural_district_id",
        "city_id",
        "village_id",
    )

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FarmRepository(db)

    def create(
        self, *, user: AuthUser, farm_id: int, payload: FarmPlotCreateIn
    ) -> FarmPlotOut:
        farm = self._farm_for_update(user.id, farm_id)
        FarmService._require_active(farm)
        self._validate_geo(payload.model_dump())
        self._validate_area(farm, payload.area_sqm)
        from app.modules.farms.models import FarmPlot

        row = self.repo.add_plot(
            FarmPlot(
                farm_id=farm.id,
                **payload.model_dump(exclude={"boundary"}),
                boundary=self._boundary_json(payload.boundary),
                status=FarmStatus.ACTIVE.value,
            )
        )
        self.repo.add_audit(
            farm_id=farm.id, actor_user_id=user.id, action="plot.created",
            target_type="plot", target_id=row.id,
        )
        self.db.commit()
        self.db.refresh(row)
        return self._out(row)

    def list_own(
        self, *, user: AuthUser, farm_id: int, include_archived: bool
    ) -> list[FarmPlotOut]:
        self._farm(user.id, farm_id)
        return [
            self._out(row)
            for row in self.repo.list_owned_plots(
                farm_id=farm_id,
                owner_user_id=user.id,
                include_archived=include_archived,
            )
        ]

    def get_own(self, *, user: AuthUser, farm_id: int, plot_id: int) -> FarmPlotOut:
        return self._out(self._plot(user.id, farm_id, plot_id))

    def update(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        plot_id: int,
        payload: FarmPlotUpdateIn,
    ) -> FarmPlotOut:
        farm = self._farm_for_update(user.id, farm_id)
        FarmService._require_active(farm)
        row = self._plot(user.id, farm_id, plot_id, for_update=True)
        FarmService._require_active(row)
        changes = payload.model_dump(exclude_unset=True, exclude={"boundary"})
        geo = {field: changes.get(field, getattr(row, field)) for field in self._geo_fields}
        self._validate_geo(geo)
        latitude = changes.get("latitude", row.latitude)
        longitude = changes.get("longitude", row.longitude)
        if (latitude is None) != (longitude is None):
            raise AppException(
                code="FARM_PLOT_COORDINATE_PAIR_REQUIRED",
                message="Latitude and longitude must be provided together",
                status_code=422,
            )
        area = changes.get("area_sqm", row.area_sqm)
        self._validate_area(farm, area, exclude_plot_id=row.id)
        for field, value in changes.items():
            setattr(row, field, value)
        if "boundary" in payload.model_fields_set:
            row.boundary = self._boundary_json(payload.boundary)
        self.repo.add_audit(
            farm_id=farm.id, actor_user_id=user.id, action="plot.updated",
            target_type="plot", target_id=row.id,
            details={"fields": sorted(payload.model_fields_set)},
        )
        self.db.commit()
        self.db.refresh(row)
        return self._out(row)

    def archive(
        self, *, user: AuthUser, farm_id: int, plot_id: int, reason: str | None
    ) -> FarmPlotOut:
        farm = self._farm_for_update(user.id, farm_id)
        FarmService._require_active(farm)
        row = self._plot(user.id, farm_id, plot_id, for_update=True)
        FarmService._require_active(row)
        row.status = FarmStatus.ARCHIVED.value
        row.archived_at = datetime.now(UTC).replace(tzinfo=None)
        row.archive_reason = reason
        self.repo.add_audit(
            farm_id=farm.id, actor_user_id=user.id, action="plot.archived",
            target_type="plot", target_id=row.id,
        )
        self.db.commit()
        self.db.refresh(row)
        return self._out(row)

    def restore(self, *, user: AuthUser, farm_id: int, plot_id: int) -> FarmPlotOut:
        farm = self._farm_for_update(user.id, farm_id)
        FarmService._require_active(farm)
        row = self._plot(user.id, farm_id, plot_id, for_update=True)
        if row.status != FarmStatus.ARCHIVED.value:
            raise AppException("FARM_PLOT_NOT_ARCHIVED", "Plot is not archived", 409)
        self._validate_area(farm, row.area_sqm, exclude_plot_id=row.id)
        row.status = FarmStatus.ACTIVE.value
        row.archived_at = None
        row.archive_reason = None
        self.repo.add_audit(
            farm_id=farm.id, actor_user_id=user.id, action="plot.restored",
            target_type="plot", target_id=row.id,
        )
        self.db.commit()
        self.db.refresh(row)
        return self._out(row)

    def _farm(self, user_id: int, farm_id: int) -> Farm:
        row = self.repo.get_owned(farm_id=farm_id, owner_user_id=user_id)
        if row is None:
            raise AppException("FARM_NOT_FOUND", "Farm not found", 404)
        return row

    def _farm_for_update(self, user_id: int, farm_id: int) -> Farm:
        row = self.repo.get_owned_for_update(farm_id=farm_id, owner_user_id=user_id)
        if row is None:
            raise AppException("FARM_NOT_FOUND", "Farm not found", 404)
        return row

    def _plot(
        self, user_id: int, farm_id: int, plot_id: int, for_update: bool = False
    ):
        row = self.repo.get_owned_plot(
            farm_id=farm_id,
            plot_id=plot_id,
            owner_user_id=user_id,
            for_update=for_update,
        )
        if row is None:
            raise AppException("FARM_PLOT_NOT_FOUND", "Farm plot not found", 404)
        return row

    def _validate_area(
        self, farm: Farm, area: Decimal, exclude_plot_id: int | None = None
    ) -> None:
        if farm.declared_area_sqm is None:
            return
        used = self.repo.total_plot_area(
            farm_id=farm.id, exclude_plot_id=exclude_plot_id
        )
        if used + area > farm.declared_area_sqm:
            raise AppException(
                "FARM_PLOT_AREA_EXCEEDS_FARM",
                "Total plot area exceeds declared farm area",
                409,
                {
                    "declared_area_sqm": str(farm.declared_area_sqm),
                    "resulting_plot_area_sqm": str(used + area),
                },
            )

    def _validate_geo(self, values: dict) -> None:
        if any(
            values.get(field) is not None
            for field in (
                "county_id",
                "district_id",
                "rural_district_id",
                "city_id",
                "village_id",
            )
        ) and values.get("province_id") is None:
            raise AppException(
                "FARM_PLOT_GEO_PARENT_REQUIRED",
                "province_id is required for the selected Geo hierarchy",
                422,
            )
        if any(
            values.get(field) is not None
            for field in ("district_id", "rural_district_id", "city_id", "village_id")
        ) and values.get("county_id") is None:
            raise AppException(
                "FARM_PLOT_GEO_PARENT_REQUIRED",
                "county_id is required for the selected Geo hierarchy",
                422,
            )
        if (
            values.get("rural_district_id") is not None
            and values.get("district_id") is None
        ):
            raise AppException(
                "FARM_PLOT_GEO_PARENT_REQUIRED",
                "district_id is required for rural_district_id",
                422,
            )
        rows = {}
        getters = {
            "province_id": self.repo.get_province,
            "county_id": self.repo.get_county,
            "district_id": self.repo.get_district,
            "rural_district_id": self.repo.get_rural_district,
            "city_id": self.repo.get_city,
            "village_id": self.repo.get_village,
        }
        for field, getter in getters.items():
            geo_id = values.get(field)
            if geo_id is not None:
                rows[field] = getter(geo_id)
                if rows[field] is None:
                    raise AppException(
                        "FARM_PLOT_GEO_INVALID",
                        f"Invalid {field}",
                        422,
                        {"field": field},
                    )
        parents = {
            "county_id": ("province_id",),
            "district_id": ("province_id", "county_id"),
            "rural_district_id": ("province_id", "county_id", "district_id"),
            "city_id": ("province_id", "county_id", "district_id"),
            "village_id": (
                "province_id",
                "county_id",
                "district_id",
                "rural_district_id",
            ),
        }
        for child, parent_fields in parents.items():
            row = rows.get(child)
            if row is None:
                continue
            for parent in parent_fields:
                expected = values.get(parent)
                actual = getattr(row, parent, None)
                if expected is not None and actual != expected:
                    raise AppException(
                        "FARM_PLOT_GEO_MISMATCH",
                        "Geo hierarchy is inconsistent",
                        422,
                        {"child": child, "parent": parent},
                    )

    @staticmethod
    def _boundary_json(boundary):
        if boundary is None:
            return None
        return [point.model_dump(mode="json") for point in boundary]

    @staticmethod
    def _out(row) -> FarmPlotOut:
        return FarmPlotOut(
            id=row.id,
            farm_id=row.farm_id,
            name=row.name,
            description=row.description,
            area_sqm=row.area_sqm,
            province_id=row.province_id,
            county_id=row.county_id,
            district_id=row.district_id,
            rural_district_id=row.rural_district_id,
            city_id=row.city_id,
            village_id=row.village_id,
            latitude=row.latitude,
            longitude=row.longitude,
            boundary=row.boundary,
            status=FarmStatus(row.status),
            archived_at=row.archived_at,
            archive_reason=row.archive_reason,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class FarmCropReferenceService:
    def __init__(self, db: Session) -> None:
        self.repo = FarmRepository(db)

    def categories(self) -> list[CropCategoryOut]:
        return [CropCategoryOut.model_validate(row, from_attributes=True) for row in self.repo.list_crop_categories()]

    def measurement_units(self, dimension: str | None) -> list[MeasurementUnitOut]:
        if dimension is not None and dimension not in {
            "area", "mass", "volume", "count", "length"
        }:
            raise AppException(
                "FARM_MEASUREMENT_DIMENSION_INVALID",
                "Unsupported measurement dimension",
                422,
            )
        return [
            MeasurementUnitOut.model_validate(row, from_attributes=True)
            for row in self.repo.list_measurement_units(dimension)
        ]

    def crops(self, category_id: int | None) -> list[CropOut]:
        return [CropOut.model_validate(row, from_attributes=True) for row in self.repo.list_crops(category_id)]

    def varieties(self, crop_id: int) -> list[CropVarietyOut]:
        if self.repo.get_crop(crop_id) is None:
            raise AppException("FARM_CROP_NOT_FOUND", "Crop not found", 404)
        return [CropVarietyOut.model_validate(row, from_attributes=True) for row in self.repo.list_varieties(crop_id)]


class FarmCropCycleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FarmRepository(db)
        self.plot_service = FarmPlotService(db)
        self.plot_service.repo = self.repo

    def create(self, *, user: AuthUser, farm_id: int, plot_id: int, payload: FarmCropCycleCreateIn) -> FarmCropCycleOut:
        farm = self.plot_service._farm_for_update(user.id, farm_id)
        FarmService._require_active(farm)
        plot = self.plot_service._plot(user.id, farm_id, plot_id, for_update=True)
        FarmService._require_active(plot)
        self._validate_reference(payload.crop_id, payload.variety_id)
        self._validate_overlap(
            plot_id=plot_id,
            starts_on=payload.planned_start_date,
            ends_on=payload.planned_end_date,
            mode=payload.cultivation_mode.value,
        )
        row = self.repo.add_cycle(
            FarmCropCycle(
                plot_id=plot_id,
                crop_id=payload.crop_id,
                variety_id=payload.variety_id,
                title=payload.title,
                cultivation_mode=payload.cultivation_mode.value,
                planned_start_date=payload.planned_start_date,
                planned_end_date=payload.planned_end_date,
                status=CropCycleStatus.PLANNED.value,
                notes=payload.notes,
            )
        )
        self.repo.add_audit(
            farm_id=farm_id, actor_user_id=user.id, action="cycle.created",
            target_type="crop_cycle", target_id=row.id,
        )
        self.db.commit()
        self.db.refresh(row)
        return self._out(row)

    def list_own(self, *, user: AuthUser, farm_id: int, plot_id: int) -> list[FarmCropCycleOut]:
        self.plot_service._plot(user.id, farm_id, plot_id)
        return [self._out(row) for row in self.repo.list_owned_cycles(
            farm_id=farm_id, plot_id=plot_id, owner_user_id=user.id
        )]

    def get_own(self, *, user: AuthUser, farm_id: int, plot_id: int, cycle_id: int) -> FarmCropCycleOut:
        return self._out(self._cycle(user.id, farm_id, plot_id, cycle_id))

    def update(self, *, user: AuthUser, farm_id: int, plot_id: int, cycle_id: int, payload: FarmCropCycleUpdateIn) -> FarmCropCycleOut:
        self.plot_service._farm_for_update(user.id, farm_id)
        row = self._cycle(user.id, farm_id, plot_id, cycle_id, True)
        if row.status != CropCycleStatus.PLANNED.value:
            raise AppException("FARM_CROP_CYCLE_NOT_EDITABLE", "Only planned cycles can be edited", 409)
        changes = payload.model_dump(exclude_unset=True)
        crop_id = changes.get("crop_id", row.crop_id)
        variety_id = changes.get("variety_id", row.variety_id)
        starts_on = changes.get("planned_start_date", row.planned_start_date)
        ends_on = changes.get("planned_end_date", row.planned_end_date)
        mode = changes.get("cultivation_mode", row.cultivation_mode)
        mode = mode.value if isinstance(mode, CultivationMode) else mode
        if ends_on < starts_on:
            raise AppException("FARM_CROP_CYCLE_DATES_INVALID", "Cycle end date cannot precede start date", 422)
        self._validate_reference(crop_id, variety_id)
        self._validate_overlap(
            plot_id=plot_id, starts_on=starts_on, ends_on=ends_on,
            mode=mode, exclude_cycle_id=row.id
        )
        for field, value in changes.items():
            setattr(row, field, value.value if isinstance(value, CultivationMode) else value)
        self.repo.add_audit(
            farm_id=farm_id, actor_user_id=user.id, action="cycle.updated",
            target_type="crop_cycle", target_id=row.id,
            details={"fields": sorted(changes)},
        )
        self.db.commit()
        self.db.refresh(row)
        return self._out(row)

    def transition(self, *, user: AuthUser, farm_id: int, plot_id: int, cycle_id: int, action: str, effective_date) -> FarmCropCycleOut:
        self.plot_service._farm_for_update(user.id, farm_id)
        row = self._cycle(user.id, farm_id, plot_id, cycle_id, True)
        if action == "start" and row.status == "planned":
            row.status = "active"
            row.actual_start_date = effective_date
        elif action == "complete" and row.status == "active":
            if effective_date < row.actual_start_date:
                raise AppException("FARM_CROP_CYCLE_DATES_INVALID", "Completion date cannot precede start date", 422)
            row.status = "completed"
            row.actual_end_date = effective_date
        elif action == "cancel" and row.status in ("planned", "active"):
            row.status = "cancelled"
        else:
            raise AppException("FARM_CROP_CYCLE_TRANSITION_INVALID", "Invalid crop cycle transition", 409)
        self.repo.add_audit(
            farm_id=farm_id, actor_user_id=user.id, action=f"cycle.{action}",
            target_type="crop_cycle", target_id=row.id,
            details={"effective_date": effective_date.isoformat()},
        )
        self.db.commit()
        self.db.refresh(row)
        return self._out(row)

    def _cycle(self, user_id, farm_id, plot_id, cycle_id, for_update=False):
        row = self.repo.get_owned_cycle(
            farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id,
            owner_user_id=user_id, for_update=for_update
        )
        if row is None:
            raise AppException("FARM_CROP_CYCLE_NOT_FOUND", "Crop cycle not found", 404)
        return row

    def _validate_reference(self, crop_id: int, variety_id: int | None) -> None:
        if self.repo.get_crop(crop_id) is None:
            raise AppException("FARM_CROP_NOT_FOUND", "Crop not found", 422)
        if variety_id is not None:
            variety = self.repo.get_variety(variety_id)
            if variety is None or variety.crop_id != crop_id:
                raise AppException("FARM_CROP_VARIETY_MISMATCH", "Variety does not belong to crop", 422)

    def _validate_overlap(self, *, plot_id, starts_on, ends_on, mode, exclude_cycle_id=None):
        conflicts = self.repo.overlapping_cycles(
            plot_id=plot_id, starts_on=starts_on, ends_on=ends_on,
            exclude_cycle_id=exclude_cycle_id
        )
        if conflicts and (
            mode != CultivationMode.INTERCROP.value
            or any(row.cultivation_mode != CultivationMode.INTERCROP.value for row in conflicts)
        ):
            raise AppException(
                "FARM_CROP_CYCLE_OVERLAP",
                "Overlapping cycles require explicit intercrop mode on every cycle",
                409,
            )

    @staticmethod
    def _out(row) -> FarmCropCycleOut:
        status = CropCycleStatus(row.status)
        return FarmCropCycleOut(
            id=row.id, plot_id=row.plot_id, crop_id=row.crop_id,
            variety_id=row.variety_id, title=row.title,
            cultivation_mode=CultivationMode(row.cultivation_mode),
            planned_start_date=row.planned_start_date,
            planned_end_date=row.planned_end_date,
            actual_start_date=row.actual_start_date,
            actual_end_date=row.actual_end_date,
            status=status, notes=row.notes,
            can_edit=status == CropCycleStatus.PLANNED,
            can_start=status == CropCycleStatus.PLANNED,
            can_complete=status == CropCycleStatus.ACTIVE,
            can_cancel=status in (CropCycleStatus.PLANNED, CropCycleStatus.ACTIVE),
            created_at=row.created_at, updated_at=row.updated_at,
        )


class FarmEnvironmentService:
    _metric_units = {
        ("soil", "ph"): "ph",
        ("soil", "electrical_conductivity"): "ds_m",
        ("soil", "organic_matter"): "percent",
        ("soil", "nitrogen"): "mg_kg",
        ("soil", "phosphorus"): "mg_kg",
        ("soil", "potassium"): "mg_kg",
        ("water", "ph"): "ph",
        ("water", "electrical_conductivity"): "ds_m",
        ("water", "tds"): "mg_l",
        ("water", "sar"): "ratio",
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FarmRepository(db)
        self.plot_service = FarmPlotService(db)
        self.plot_service.repo = self.repo

    def upsert_soil(self, *, user, farm_id, plot_id, payload: SoilProfileIn):
        self._active_plot(user.id, farm_id, plot_id)
        row = self.repo.get_soil_profile(plot_id)
        if row is None:
            row = self.repo.add(FarmSoilProfile(plot_id=plot_id))
        for field, value in payload.model_dump().items():
            setattr(row, field, value.value if hasattr(value, "value") else value)
        self._commit(row, user.id, farm_id, "soil_profile.upserted", "soil_profile")
        return SoilProfileOut.model_validate(row, from_attributes=True)

    def get_soil(self, *, user, farm_id, plot_id):
        self.plot_service._plot(user.id, farm_id, plot_id)
        row = self.repo.get_soil_profile(plot_id)
        if row is None:
            raise AppException("FARM_SOIL_PROFILE_NOT_FOUND", "Soil profile not found", 404)
        return SoilProfileOut.model_validate(row, from_attributes=True)

    def upsert_irrigation(self, *, user, farm_id, plot_id, payload: IrrigationProfileIn):
        self._active_plot(user.id, farm_id, plot_id)
        if payload.water_source_id is not None:
            source = self.repo.get_water_source(
                farm_id=farm_id, source_id=payload.water_source_id
            )
            if source is None or source.status != FarmStatus.ACTIVE.value:
                raise AppException("FARM_WATER_SOURCE_INVALID", "Active water source not found in farm", 422)
        row = self.repo.get_irrigation_profile(plot_id)
        if row is None:
            row = self.repo.add(FarmIrrigationProfile(plot_id=plot_id))
        for field, value in payload.model_dump().items():
            setattr(row, field, value.value if hasattr(value, "value") else value)
        self._commit(
            row, user.id, farm_id, "irrigation_profile.upserted", "irrigation_profile"
        )
        return IrrigationProfileOut.model_validate(row, from_attributes=True)

    def get_irrigation(self, *, user, farm_id, plot_id):
        self.plot_service._plot(user.id, farm_id, plot_id)
        row = self.repo.get_irrigation_profile(plot_id)
        if row is None:
            raise AppException("FARM_IRRIGATION_PROFILE_NOT_FOUND", "Irrigation profile not found", 404)
        return IrrigationProfileOut.model_validate(row, from_attributes=True)

    def create_water(self, *, user, farm_id, payload: WaterSourceIn):
        farm = self.plot_service._farm_for_update(user.id, farm_id)
        FarmService._require_active(farm)
        row = self.repo.add(FarmWaterSource(
            farm_id=farm_id, name=payload.name, source_type=payload.source_type.value,
            notes=payload.notes, status=FarmStatus.ACTIVE.value
        ))
        self._commit(row, user.id, farm_id, "water_source.created", "water_source")
        return WaterSourceOut.model_validate(row, from_attributes=True)

    def list_water(self, *, user, farm_id):
        self.plot_service._farm(user.id, farm_id)
        return [WaterSourceOut.model_validate(row, from_attributes=True) for row in self.repo.list_water_sources(farm_id)]

    def archive_water(self, *, user, farm_id, source_id):
        self.plot_service._farm_for_update(user.id, farm_id)
        row = self.repo.get_water_source(farm_id=farm_id, source_id=source_id, for_update=True)
        if row is None:
            raise AppException("FARM_WATER_SOURCE_NOT_FOUND", "Water source not found", 404)
        if row.status != FarmStatus.ACTIVE.value:
            raise AppException("FARM_WATER_SOURCE_ARCHIVED", "Water source is already archived", 409)
        row.status = FarmStatus.ARCHIVED.value
        row.archived_at = datetime.now(UTC).replace(tzinfo=None)
        self._commit(row, user.id, farm_id, "water_source.archived", "water_source")
        return WaterSourceOut.model_validate(row, from_attributes=True)

    def create_observation(self, *, user, farm_id, payload: LabObservationCreateIn):
        self.plot_service._farm(user.id, farm_id)
        subject = payload.subject_type.value
        expected_unit = self._metric_units.get((subject, payload.metric_code.value))
        if expected_unit is None:
            raise AppException("FARM_LAB_METRIC_SUBJECT_INVALID", "Metric is not valid for subject", 422)
        if payload.unit_code.lower() != expected_unit:
            raise AppException(
                "FARM_LAB_UNIT_INVALID", "Metric requires its canonical unit", 422,
                {"expected_unit": expected_unit}
            )
        soil_id = water_id = None
        if payload.subject_type == LabSubjectType.SOIL:
            row = self.repo.get_soil_profile(payload.subject_id)
            if row is None:
                raise AppException("FARM_SOIL_PROFILE_NOT_FOUND", "Soil profile not found", 404)
            self.plot_service._plot(user.id, farm_id, row.plot_id)
            soil_id = row.id
        else:
            row = self.repo.get_water_source(farm_id=farm_id, source_id=payload.subject_id)
            if row is None:
                raise AppException("FARM_WATER_SOURCE_NOT_FOUND", "Water source not found", 404)
            water_id = row.id
        observation = self.repo.add(FarmLabObservation(
            soil_profile_id=soil_id, water_source_id=water_id,
            metric_code=payload.metric_code.value, value=payload.value,
            unit_code=expected_unit, sampled_on=payload.sampled_on,
            tested_on=payload.tested_on, laboratory_name=payload.laboratory_name,
            notes=payload.notes
        ))
        self._commit(
            observation, user.id, farm_id, "lab_observation.created", "lab_observation"
        )
        return self._observation_out(observation, payload.subject_type, payload.subject_id)

    def list_observations(self, *, user, farm_id, subject_type, subject_id):
        self.plot_service._farm(user.id, farm_id)
        soil_id = water_id = None
        if subject_type == LabSubjectType.SOIL:
            soil = self.repo.get_soil_profile(subject_id)
            if soil is None:
                raise AppException("FARM_SOIL_PROFILE_NOT_FOUND", "Soil profile not found", 404)
            self.plot_service._plot(user.id, farm_id, soil.plot_id)
            soil_id = soil.id
        else:
            source = self.repo.get_water_source(farm_id=farm_id, source_id=subject_id)
            if source is None:
                raise AppException("FARM_WATER_SOURCE_NOT_FOUND", "Water source not found", 404)
            water_id = source.id
        return [
            self._observation_out(row, subject_type, subject_id)
            for row in self.repo.list_lab_observations(
                soil_profile_id=soil_id, water_source_id=water_id
            )
        ]

    def _active_plot(self, user_id, farm_id, plot_id):
        farm = self.plot_service._farm_for_update(user_id, farm_id)
        FarmService._require_active(farm)
        plot = self.plot_service._plot(user_id, farm_id, plot_id, True)
        FarmService._require_active(plot)

    def _commit(self, row, actor_user_id, farm_id, action, target_type):
        self.repo.add_audit(
            farm_id=farm_id, actor_user_id=actor_user_id, action=action,
            target_type=target_type, target_id=row.id,
        )
        self.db.commit()
        self.db.refresh(row)

    @staticmethod
    def _observation_out(row, subject_type, subject_id):
        return LabObservationOut(
            id=row.id, subject_type=subject_type, subject_id=subject_id,
            metric_code=row.metric_code, value=row.value, unit_code=row.unit_code,
            sampled_on=row.sampled_on, tested_on=row.tested_on,
            laboratory_name=row.laboratory_name, notes=row.notes,
            created_at=row.created_at, updated_at=row.updated_at
        )
