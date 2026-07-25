from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.auth.models import AuthUser
from app.modules.farms.enums import (
    CropCycleStatus,
    FarmRecordSubjectType,
)
from app.modules.farms.models import (
    FarmHarvestObservation,
    FarmMeasurementUnit,
    FarmOperation,
    FarmOperationInput,
    FarmRecordMedia,
)
from app.modules.farms.repository import FarmRepository
from app.modules.farms.schemas import (
    FarmHarvestCreateIn,
    FarmHarvestOut,
    FarmOperationCreateIn,
    FarmOperationInputCreateIn,
    FarmOperationInputOut,
    FarmOperationOut,
    FarmRecordMediaCreateIn,
    FarmRecordMediaOut,
)
from app.modules.farms.service import FarmCropCycleService
from app.modules.media.enums import MediaPurpose, MediaStatus, MediaVisibility
from app.modules.media.models import MediaFile


class FarmDiaryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FarmRepository(db)
        self.cycles = FarmCropCycleService(db)
        self.cycles.repo = self.repo
        self.cycles.plot_service.repo = self.repo

    def create_operation(
        self, *, user: AuthUser, farm_id: int, plot_id: int, cycle_id: int,
        payload: FarmOperationCreateIn,
    ) -> FarmOperationOut:
        cycle = self._active_cycle(user.id, farm_id, plot_id, cycle_id, True)
        if payload.occurred_on < cycle.actual_start_date:
            raise AppException(
                "FARM_OPERATION_DATE_INVALID",
                "Operation date cannot precede cycle start date",
                422,
            )
        row = self.repo.add(FarmOperation(
            cycle_id=cycle.id,
            operation_type=payload.operation_type.value,
            title=payload.title,
            occurred_on=payload.occurred_on,
            notes=payload.notes,
        ))
        self._commit(row, user.id, farm_id, "operation.created", "operation")
        return self._operation_out(row)

    def list_operations(
        self, *, user: AuthUser, farm_id: int, plot_id: int, cycle_id: int,
    ) -> list[FarmOperationOut]:
        self.cycles._cycle(user.id, farm_id, plot_id, cycle_id)
        rows = (
            self.db.query(FarmOperation)
            .filter(FarmOperation.cycle_id == cycle_id)
            .order_by(FarmOperation.occurred_on.desc(), FarmOperation.id.desc())
            .all()
        )
        return [self._operation_out(row) for row in rows]

    def add_input(
        self, *, user: AuthUser, farm_id: int, plot_id: int, cycle_id: int,
        operation_id: int, payload: FarmOperationInputCreateIn,
    ) -> FarmOperationInputOut:
        self._active_cycle(user.id, farm_id, plot_id, cycle_id, True)
        operation = self._operation(cycle_id, operation_id)
        unit = self._unit(payload.measurement_unit_id)
        row = self.repo.add(FarmOperationInput(
            operation_id=operation.id,
            name=payload.name,
            quantity=payload.quantity,
            measurement_unit_id=unit.id,
            notes=payload.notes,
        ))
        self._commit(row, user.id, farm_id, "operation_input.created", "operation_input")
        return self._input_out(row, unit)

    def create_harvest(
        self, *, user: AuthUser, farm_id: int, plot_id: int, cycle_id: int,
        payload: FarmHarvestCreateIn,
    ) -> FarmHarvestOut:
        cycle = self._active_cycle(user.id, farm_id, plot_id, cycle_id, True)
        if payload.harvested_on < cycle.actual_start_date:
            raise AppException(
                "FARM_HARVEST_DATE_INVALID",
                "Harvest date cannot precede cycle start date",
                422,
            )
        unit = self._unit(payload.measurement_unit_id)
        if unit.dimension not in ("mass", "count"):
            raise AppException(
                "FARM_HARVEST_UNIT_INVALID",
                "Harvest unit dimension must be mass or count",
                422,
            )
        row = self.repo.add(FarmHarvestObservation(
            cycle_id=cycle.id,
            harvested_on=payload.harvested_on,
            quantity=payload.quantity,
            measurement_unit_id=unit.id,
            quality_grade=payload.quality_grade,
            notes=payload.notes,
        ))
        self._commit(row, user.id, farm_id, "harvest.created", "harvest")
        return self._harvest_out(row, unit)

    def list_harvests(
        self, *, user: AuthUser, farm_id: int, plot_id: int, cycle_id: int,
    ) -> list[FarmHarvestOut]:
        self.cycles._cycle(user.id, farm_id, plot_id, cycle_id)
        rows = (
            self.db.query(FarmHarvestObservation, FarmMeasurementUnit)
            .join(FarmMeasurementUnit, FarmMeasurementUnit.id == FarmHarvestObservation.measurement_unit_id)
            .filter(FarmHarvestObservation.cycle_id == cycle_id)
            .order_by(FarmHarvestObservation.harvested_on.desc(), FarmHarvestObservation.id.desc())
            .all()
        )
        return [self._harvest_out(row, unit) for row, unit in rows]

    def attach_media(
        self, *, user: AuthUser, farm_id: int, plot_id: int, cycle_id: int,
        payload: FarmRecordMediaCreateIn,
    ) -> FarmRecordMediaOut:
        self._active_cycle(user.id, farm_id, plot_id, cycle_id, True)
        subject_fields = {"cycle_id": None, "operation_id": None, "harvest_id": None}
        if payload.subject_type == FarmRecordSubjectType.CYCLE:
            if payload.subject_id != cycle_id:
                raise AppException("FARM_MEDIA_SUBJECT_INVALID", "Cycle subject does not match route", 422)
            subject_fields["cycle_id"] = cycle_id
        elif payload.subject_type == FarmRecordSubjectType.OPERATION:
            self._operation(cycle_id, payload.subject_id)
            subject_fields["operation_id"] = payload.subject_id
        else:
            self._harvest(cycle_id, payload.subject_id)
            subject_fields["harvest_id"] = payload.subject_id

        media = self.db.query(MediaFile).filter(MediaFile.id == payload.media_file_id).one_or_none()
        if (
            media is None
            or media.owner_user_id != user.id
            or media.status != MediaStatus.ACTIVE.value
            or media.visibility != MediaVisibility.PRIVATE.value
            or media.purpose != MediaPurpose.FARM_RECORD.value
        ):
            raise AppException(
                "FARM_MEDIA_FILE_INVALID",
                "Active private farm-record media owned by the current user is required",
                422,
            )
        duplicate = self.db.query(FarmRecordMedia).filter(
            getattr(FarmRecordMedia, f"{payload.subject_type.value}_id") == payload.subject_id,
            FarmRecordMedia.media_file_id == payload.media_file_id,
        ).first()
        if duplicate is not None:
            raise AppException("FARM_MEDIA_ALREADY_ATTACHED", "Media is already attached", 409)
        row = self.repo.add(FarmRecordMedia(
            media_file_id=media.id, caption=payload.caption, **subject_fields
        ))
        self._commit(row, user.id, farm_id, "record_media.attached", "record_media")
        return self._media_out(row)

    def list_media(
        self, *, user: AuthUser, farm_id: int, plot_id: int, cycle_id: int,
    ) -> list[FarmRecordMediaOut]:
        self.cycles._cycle(user.id, farm_id, plot_id, cycle_id)
        operation_ids = self.db.query(FarmOperation.id).filter(FarmOperation.cycle_id == cycle_id)
        harvest_ids = self.db.query(FarmHarvestObservation.id).filter(
            FarmHarvestObservation.cycle_id == cycle_id
        )
        rows = self.db.query(FarmRecordMedia).filter(
            (FarmRecordMedia.cycle_id == cycle_id)
            | (FarmRecordMedia.operation_id.in_(operation_ids))
            | (FarmRecordMedia.harvest_id.in_(harvest_ids))
        ).order_by(FarmRecordMedia.id.desc()).all()
        return [self._media_out(row) for row in rows]

    def _active_cycle(self, user_id, farm_id, plot_id, cycle_id, for_update=False):
        cycle = self.cycles._cycle(user_id, farm_id, plot_id, cycle_id, for_update)
        if cycle.status != CropCycleStatus.ACTIVE.value:
            raise AppException(
                "FARM_CROP_CYCLE_NOT_ACTIVE",
                "Diary records can only be added to an active crop cycle",
                409,
            )
        return cycle

    def _operation(self, cycle_id: int, operation_id: int) -> FarmOperation:
        row = self.db.query(FarmOperation).filter(
            FarmOperation.id == operation_id, FarmOperation.cycle_id == cycle_id
        ).one_or_none()
        if row is None:
            raise AppException("FARM_OPERATION_NOT_FOUND", "Farm operation not found", 404)
        return row

    def _harvest(self, cycle_id: int, harvest_id: int) -> FarmHarvestObservation:
        row = self.db.query(FarmHarvestObservation).filter(
            FarmHarvestObservation.id == harvest_id,
            FarmHarvestObservation.cycle_id == cycle_id,
        ).one_or_none()
        if row is None:
            raise AppException("FARM_HARVEST_NOT_FOUND", "Harvest observation not found", 404)
        return row

    def _unit(self, unit_id: int) -> FarmMeasurementUnit:
        row = self.db.query(FarmMeasurementUnit).filter(
            FarmMeasurementUnit.id == unit_id,
            FarmMeasurementUnit.is_active.is_(True),
        ).one_or_none()
        if row is None:
            raise AppException("FARM_MEASUREMENT_UNIT_NOT_FOUND", "Measurement unit not found", 422)
        return row

    def _operation_out(self, row: FarmOperation) -> FarmOperationOut:
        input_rows = (
            self.db.query(FarmOperationInput, FarmMeasurementUnit)
            .join(FarmMeasurementUnit, FarmMeasurementUnit.id == FarmOperationInput.measurement_unit_id)
            .filter(FarmOperationInput.operation_id == row.id)
            .order_by(FarmOperationInput.id)
            .all()
        )
        return FarmOperationOut(
            id=row.id, cycle_id=row.cycle_id, operation_type=row.operation_type,
            title=row.title, occurred_on=row.occurred_on, notes=row.notes,
            inputs=[self._input_out(item, unit) for item, unit in input_rows],
            created_at=row.created_at, updated_at=row.updated_at,
        )

    @staticmethod
    def _input_out(row, unit) -> FarmOperationInputOut:
        return FarmOperationInputOut(
            id=row.id, operation_id=row.operation_id, name=row.name,
            quantity=row.quantity, measurement_unit_id=row.measurement_unit_id,
            unit_code=unit.code, unit_symbol=unit.symbol, notes=row.notes,
            created_at=row.created_at,
        )

    @staticmethod
    def _harvest_out(row, unit) -> FarmHarvestOut:
        return FarmHarvestOut(
            id=row.id, cycle_id=row.cycle_id, harvested_on=row.harvested_on,
            quantity=row.quantity, measurement_unit_id=row.measurement_unit_id,
            unit_code=unit.code, unit_symbol=unit.symbol,
            quality_grade=row.quality_grade, notes=row.notes, created_at=row.created_at,
        )

    @staticmethod
    def _media_out(row: FarmRecordMedia) -> FarmRecordMediaOut:
        if row.cycle_id is not None:
            subject_type, subject_id = FarmRecordSubjectType.CYCLE, row.cycle_id
        elif row.operation_id is not None:
            subject_type, subject_id = FarmRecordSubjectType.OPERATION, row.operation_id
        else:
            subject_type, subject_id = FarmRecordSubjectType.HARVEST, row.harvest_id
        return FarmRecordMediaOut(
            id=row.id, subject_type=subject_type, subject_id=subject_id,
            media_file_id=row.media_file_id, caption=row.caption, created_at=row.created_at,
        )

    def _commit(
        self, row, actor_user_id: int, farm_id: int, action: str, target_type: str
    ) -> None:
        self.repo.add_audit(
            farm_id=farm_id, actor_user_id=actor_user_id, action=action,
            target_type=target_type, target_id=row.id,
        )
        self.db.commit()
        self.db.refresh(row)
