from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.auth.models import AuthUser
from app.modules.farms.enums import FarmStatus
from app.modules.farms.models import Farm
from app.modules.farms.repository import FarmRepository
from app.modules.farms.schemas import (
    FarmArchiveIn,
    FarmCreateIn,
    FarmOwnerOut,
    FarmPlotCreateIn,
    FarmPlotOut,
    FarmPlotUpdateIn,
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
