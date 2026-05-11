from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import AuthUser
from app.modules.profiles.schemas import (
    VerificationAttachDocumentIn,
    VerificationCancelIn,
    VerificationCreateIn,
)
from app.modules.profiles.service import ProfileService


router = APIRouter(
    prefix="/verifications",
    tags=["Verifications"],
)


@router.post("")
def create_verification_request(
    payload: VerificationCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)

    result = service.create_my_verification_request(
        user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Verification request created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/me")
def list_my_verification_requests(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)

    result = service.list_my_verification_requests(user=current_user)

    return success_response(
        data=[item.model_dump(mode="json") for item in result],
        message="OK",
        meta={
            "count": len(result),
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/{request_id}")
def get_my_verification_request(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)

    result = service.get_my_verification_request(
        user=current_user,
        request_id=request_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/{request_id}/documents")
def attach_document_to_verification_request(
    request_id: int,
    payload: VerificationAttachDocumentIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)

    result = service.attach_document_to_my_verification_request(
        user=current_user,
        request_id=request_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Document attached to verification request",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/{request_id}/submit")
def submit_verification_request(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)

    result = service.submit_my_verification_request(
        user=current_user,
        request_id=request_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Verification request submitted",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/{request_id}/cancel")
def cancel_verification_request(
    request_id: int,
    payload: VerificationCancelIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)

    result = service.cancel_my_verification_request(
        user=current_user,
        request_id=request_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Verification request cancelled",
        meta={"trace_id": request.state.trace_id},
    )
