from datetime import UTC, datetime

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
            status=FarmStatus(row.status),
            archived_at=row.archived_at,
            archive_reason=row.archive_reason,
            can_edit=active,
            can_archive=active,
            can_restore=not active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
