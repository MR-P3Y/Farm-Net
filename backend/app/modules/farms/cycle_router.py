from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.farms.schemas import (
    FarmCropCycleCreateIn,
    FarmCropCycleDetailResponse,
    FarmCropCycleListResponse,
    FarmCropCycleTransitionIn,
    FarmCropCycleUpdateIn,
    MeasurementUnitOut,
)
from app.modules.farms.service import FarmCropCycleService, FarmCropReferenceService


reference_router = APIRouter(prefix="/farm-references", tags=["Farm References"])
cycle_router = APIRouter(prefix="/farms", tags=["Farm Crop Cycles"])


@reference_router.get("/measurement-units")
def list_measurement_units(
    request: Request,
    dimension: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farm_references.read")),
):
    items: list[MeasurementUnitOut] = FarmCropReferenceService(db).measurement_units(
        dimension
    )
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"count": len(items), "trace_id": request.state.trace_id},
    )


@reference_router.get("/crop-categories")
def list_crop_categories(
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farm_references.read")),
):
    items = FarmCropReferenceService(db).categories()
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"count": len(items), "trace_id": request.state.trace_id},
    )


@reference_router.get("/crops")
def list_crops(
    request: Request,
    category_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farm_references.read")),
):
    items = FarmCropReferenceService(db).crops(category_id)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"count": len(items), "trace_id": request.state.trace_id},
    )


@reference_router.get("/crops/{crop_id}/varieties")
def list_crop_varieties(
    crop_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farm_references.read")),
):
    items = FarmCropReferenceService(db).varieties(crop_id)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"count": len(items), "trace_id": request.state.trace_id},
    )


@cycle_router.post(
    "/{farm_id}/plots/{plot_id}/cycles",
    response_model=FarmCropCycleDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_cycle(
    farm_id: int,
    plot_id: int,
    payload: FarmCropCycleCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmCropCycleService(db).create(
        user=user, farm_id=farm_id, plot_id=plot_id, payload=payload
    )
    return _response(result, "Crop cycle created", request)


@cycle_router.get(
    "/{farm_id}/plots/{plot_id}/cycles",
    response_model=FarmCropCycleListResponse,
)
def list_cycles(
    farm_id: int,
    plot_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    items = FarmCropCycleService(db).list_own(
        user=user, farm_id=farm_id, plot_id=plot_id
    )
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"count": len(items), "trace_id": request.state.trace_id},
    )


@cycle_router.get(
    "/{farm_id}/plots/{plot_id}/cycles/{cycle_id}",
    response_model=FarmCropCycleDetailResponse,
)
def get_cycle(
    farm_id: int,
    plot_id: int,
    cycle_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    result = FarmCropCycleService(db).get_own(
        user=user, farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id
    )
    return _response(result, "OK", request)


@cycle_router.patch(
    "/{farm_id}/plots/{plot_id}/cycles/{cycle_id}",
    response_model=FarmCropCycleDetailResponse,
)
def update_cycle(
    farm_id: int,
    plot_id: int,
    cycle_id: int,
    payload: FarmCropCycleUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmCropCycleService(db).update(
        user=user,
        farm_id=farm_id,
        plot_id=plot_id,
        cycle_id=cycle_id,
        payload=payload,
    )
    return _response(result, "Crop cycle updated", request)


def _transition(
    *,
    farm_id: int,
    plot_id: int,
    cycle_id: int,
    payload: FarmCropCycleTransitionIn,
    request: Request,
    db: Session,
    user: AuthUser,
    action: str,
):
    result = FarmCropCycleService(db).transition(
        user=user,
        farm_id=farm_id,
        plot_id=plot_id,
        cycle_id=cycle_id,
        action=action,
        effective_date=payload.effective_date,
    )
    return _response(result, f"Crop cycle {action}", request)


@cycle_router.post("/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/start")
def start_cycle(
    farm_id: int, plot_id: int, cycle_id: int, payload: FarmCropCycleTransitionIn,
    request: Request, db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    return _transition(farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id, payload=payload, request=request, db=db, user=user, action="start")


@cycle_router.post("/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/complete")
def complete_cycle(
    farm_id: int, plot_id: int, cycle_id: int, payload: FarmCropCycleTransitionIn,
    request: Request, db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    return _transition(farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id, payload=payload, request=request, db=db, user=user, action="complete")


@cycle_router.post("/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/cancel")
def cancel_cycle(
    farm_id: int, plot_id: int, cycle_id: int, payload: FarmCropCycleTransitionIn,
    request: Request, db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    return _transition(farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id, payload=payload, request=request, db=db, user=user, action="cancel")


def _response(result, message: str, request: Request):
    return success_response(
        data=result.model_dump(mode="json"),
        message=message,
        meta={"trace_id": request.state.trace_id},
    )
