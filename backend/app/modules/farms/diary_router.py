from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.farms.diary_service import FarmDiaryService
from app.modules.farms.schemas import (
    FarmHarvestCreateIn,
    FarmHarvestDetailResponse,
    FarmHarvestListResponse,
    FarmOperationCreateIn,
    FarmOperationDetailResponse,
    FarmOperationInputCreateIn,
    FarmOperationInputDetailResponse,
    FarmOperationListResponse,
    FarmRecordMediaCreateIn,
    FarmRecordMediaDetailResponse,
    FarmRecordMediaListResponse,
)

router = APIRouter(prefix="/farms", tags=["Farm Operation Diary"])


@router.post(
    "/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/operations",
    response_model=FarmOperationDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_operation(
    farm_id: int, plot_id: int, cycle_id: int, payload: FarmOperationCreateIn,
    request: Request, db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmDiaryService(db).create_operation(
        user=user, farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id, payload=payload
    )
    return _detail(result, "Farm operation created", request)


@router.get(
    "/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/operations",
    response_model=FarmOperationListResponse,
)
def list_operations(
    farm_id: int, plot_id: int, cycle_id: int, request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    items = FarmDiaryService(db).list_operations(
        user=user, farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id
    )
    return _list(items, request)


@router.post(
    "/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/operations/{operation_id}/inputs",
    response_model=FarmOperationInputDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_operation_input(
    farm_id: int, plot_id: int, cycle_id: int, operation_id: int,
    payload: FarmOperationInputCreateIn, request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmDiaryService(db).add_input(
        user=user, farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id,
        operation_id=operation_id, payload=payload,
    )
    return _detail(result, "Farm operation input added", request)


@router.post(
    "/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/harvests",
    response_model=FarmHarvestDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_harvest(
    farm_id: int, plot_id: int, cycle_id: int, payload: FarmHarvestCreateIn,
    request: Request, db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmDiaryService(db).create_harvest(
        user=user, farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id, payload=payload
    )
    return _detail(result, "Harvest observation created", request)


@router.get(
    "/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/harvests",
    response_model=FarmHarvestListResponse,
)
def list_harvests(
    farm_id: int, plot_id: int, cycle_id: int, request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    items = FarmDiaryService(db).list_harvests(
        user=user, farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id
    )
    return _list(items, request)


@router.post(
    "/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/media",
    response_model=FarmRecordMediaDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def attach_media(
    farm_id: int, plot_id: int, cycle_id: int, payload: FarmRecordMediaCreateIn,
    request: Request, db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmDiaryService(db).attach_media(
        user=user, farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id, payload=payload
    )
    return _detail(result, "Farm record media attached", request)


@router.get(
    "/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/media",
    response_model=FarmRecordMediaListResponse,
)
def list_media(
    farm_id: int, plot_id: int, cycle_id: int, request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    items = FarmDiaryService(db).list_media(
        user=user, farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id
    )
    return _list(items, request)


def _detail(result, message: str, request: Request):
    return success_response(
        data=result.model_dump(mode="json"), message=message,
        meta={"trace_id": request.state.trace_id},
    )


def _list(items, request: Request):
    return success_response(
        data=[item.model_dump(mode="json") for item in items], message="OK",
        meta={"count": len(items), "trace_id": request.state.trace_id},
    )
