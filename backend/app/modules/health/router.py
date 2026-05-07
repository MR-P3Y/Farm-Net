from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.health.service import get_health_status


router = APIRouter(tags=["Health"])


@router.get("/health")
def health(request: Request, db: Session = Depends(get_db)):
    trace_id = request.state.trace_id

    return success_response(
        data=get_health_status(db),
        message="OK",
        meta={"trace_id": trace_id},
    )