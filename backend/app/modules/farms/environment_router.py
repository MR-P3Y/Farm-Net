from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.farms.enums import LabSubjectType
from app.modules.farms.schemas import (
    IrrigationProfileIn,
    LabObservationCreateIn,
    SoilProfileIn,
    WaterSourceIn,
)
from app.modules.farms.service import FarmEnvironmentService


router = APIRouter(prefix="/farms", tags=["Farm Environment"])


def _one(result, message, request):
    return success_response(
        data=result.model_dump(mode="json"),
        message=message,
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/{farm_id}/plots/{plot_id}/soil-profile")
def upsert_soil(farm_id: int, plot_id: int, payload: SoilProfileIn, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("farms.manage_own"))):
    return _one(FarmEnvironmentService(db).upsert_soil(user=user, farm_id=farm_id, plot_id=plot_id, payload=payload), "Soil profile saved", request)


@router.get("/{farm_id}/plots/{plot_id}/soil-profile")
def get_soil(farm_id: int, plot_id: int, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("farms.read_own"))):
    return _one(FarmEnvironmentService(db).get_soil(user=user, farm_id=farm_id, plot_id=plot_id), "OK", request)


@router.put("/{farm_id}/plots/{plot_id}/irrigation-profile")
def upsert_irrigation(farm_id: int, plot_id: int, payload: IrrigationProfileIn, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("farms.manage_own"))):
    return _one(FarmEnvironmentService(db).upsert_irrigation(user=user, farm_id=farm_id, plot_id=plot_id, payload=payload), "Irrigation profile saved", request)


@router.get("/{farm_id}/plots/{plot_id}/irrigation-profile")
def get_irrigation(farm_id: int, plot_id: int, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("farms.read_own"))):
    return _one(FarmEnvironmentService(db).get_irrigation(user=user, farm_id=farm_id, plot_id=plot_id), "OK", request)


@router.post("/{farm_id}/water-sources")
def create_water(farm_id: int, payload: WaterSourceIn, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("farms.manage_own"))):
    return _one(FarmEnvironmentService(db).create_water(user=user, farm_id=farm_id, payload=payload), "Water source created", request)


@router.get("/{farm_id}/water-sources")
def list_water(farm_id: int, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("farms.read_own"))):
    items = FarmEnvironmentService(db).list_water(user=user, farm_id=farm_id)
    return success_response(data=[item.model_dump(mode="json") for item in items], message="OK", meta={"count": len(items), "trace_id": request.state.trace_id})


@router.post("/{farm_id}/water-sources/{source_id}/archive")
def archive_water(farm_id: int, source_id: int, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("farms.manage_own"))):
    return _one(FarmEnvironmentService(db).archive_water(user=user, farm_id=farm_id, source_id=source_id), "Water source archived", request)


@router.post("/{farm_id}/lab-observations")
def create_observation(farm_id: int, payload: LabObservationCreateIn, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("farms.manage_own"))):
    return _one(FarmEnvironmentService(db).create_observation(user=user, farm_id=farm_id, payload=payload), "Lab observation created", request)


@router.get("/{farm_id}/lab-observations/{subject_type}/{subject_id}")
def list_observations(farm_id: int, subject_type: LabSubjectType, subject_id: int, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("farms.read_own"))):
    items = FarmEnvironmentService(db).list_observations(user=user, farm_id=farm_id, subject_type=subject_type, subject_id=subject_id)
    return success_response(data=[item.model_dump(mode="json") for item in items], message="OK", meta={"count": len(items), "trace_id": request.state.trace_id})
