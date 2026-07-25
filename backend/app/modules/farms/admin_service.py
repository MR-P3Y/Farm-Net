from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.farms.enums import CropCycleStatus, FarmStatus
from app.modules.farms.models import (
    Farm,
    FarmAuditLog,
    FarmCropCycle,
    FarmPlot,
)
from app.modules.farms.schemas import (
    AdminFarmAuditOut,
    AdminFarmCycleSummaryOut,
    AdminFarmDetailOut,
    AdminFarmPlotSummaryOut,
    AdminFarmSummaryOut,
)


class AdminFarmSupportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_farms(
        self, *, q: str | None, owner_user_id: int | None,
        status: FarmStatus | None, page: int, page_size: int,
    ) -> tuple[list[AdminFarmSummaryOut], int]:
        query = self.db.query(Farm)
        if q:
            query = query.filter(
                or_(Farm.name.like(f"%{q.strip()}%"), Farm.id == _int_or_zero(q))
            )
        if owner_user_id is not None:
            query = query.filter(Farm.owner_user_id == owner_user_id)
        if status is not None:
            query = query.filter(Farm.status == status.value)
        total = query.count()
        rows = (
            query.order_by(Farm.updated_at.desc(), Farm.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return [self._summary(row) for row in rows], total

    def detail(self, farm_id: int) -> AdminFarmDetailOut:
        farm = self._farm(farm_id)
        plots = self.db.query(FarmPlot).filter(
            FarmPlot.farm_id == farm_id
        ).order_by(FarmPlot.id).all()
        cycles = (
            self.db.query(FarmCropCycle)
            .join(FarmPlot, FarmPlot.id == FarmCropCycle.plot_id)
            .filter(FarmPlot.farm_id == farm_id)
            .order_by(FarmCropCycle.id.desc())
            .all()
        )
        summary = self._summary(farm)
        cycle_counts = dict(
            self.db.query(FarmCropCycle.plot_id, func.count(FarmCropCycle.id))
            .join(FarmPlot, FarmPlot.id == FarmCropCycle.plot_id)
            .filter(FarmPlot.farm_id == farm_id)
            .group_by(FarmCropCycle.plot_id)
            .all()
        )
        return AdminFarmDetailOut(
            **summary.model_dump(),
            plots=[
                AdminFarmPlotSummaryOut(
                    id=row.id, name=row.name, area_sqm=row.area_sqm,
                    status=FarmStatus(row.status), province_id=row.province_id,
                    city_id=row.city_id, cycles_count=cycle_counts.get(row.id, 0),
                )
                for row in plots
            ],
            cycles=[
                AdminFarmCycleSummaryOut(
                    id=row.id, plot_id=row.plot_id, crop_id=row.crop_id,
                    variety_id=row.variety_id, title=row.title,
                    status=CropCycleStatus(row.status),
                    planned_start_date=row.planned_start_date,
                    planned_end_date=row.planned_end_date,
                    actual_start_date=row.actual_start_date,
                    actual_end_date=row.actual_end_date,
                )
                for row in cycles
            ],
        )

    def audit(
        self, *, farm_id: int, page: int, page_size: int
    ) -> tuple[list[AdminFarmAuditOut], int]:
        self._farm(farm_id)
        query = self.db.query(FarmAuditLog).filter(FarmAuditLog.farm_id == farm_id)
        total = query.count()
        rows = (
            query.order_by(FarmAuditLog.created_at.desc(), FarmAuditLog.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return [
            AdminFarmAuditOut.model_validate(row, from_attributes=True) for row in rows
        ], total

    def _farm(self, farm_id: int) -> Farm:
        row = self.db.query(Farm).filter(Farm.id == farm_id).one_or_none()
        if row is None:
            raise AppException("ADMIN_FARM_NOT_FOUND", "Farm not found", 404)
        return row

    def _summary(self, row: Farm) -> AdminFarmSummaryOut:
        plots_count = self.db.query(func.count(FarmPlot.id)).filter(
            FarmPlot.farm_id == row.id
        ).scalar() or 0
        cycles_count = (
            self.db.query(func.count(FarmCropCycle.id))
            .join(FarmPlot, FarmPlot.id == FarmCropCycle.plot_id)
            .filter(FarmPlot.farm_id == row.id)
            .scalar()
            or 0
        )
        return AdminFarmSummaryOut(
            id=row.id, owner_user_id=row.owner_user_id, name=row.name,
            status=FarmStatus(row.status), declared_area_sqm=row.declared_area_sqm,
            plots_count=plots_count, cycles_count=cycles_count,
            created_at=row.created_at, updated_at=row.updated_at,
        )


def _int_or_zero(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0
