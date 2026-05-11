from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import AuthUser
from app.modules.profiles.schemas import DocumentCreateIn
from app.modules.profiles.service import ProfileService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("")
def create_document(
    payload: DocumentCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)

    result = service.create_my_document(
        user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Document created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/me")
def list_my_documents(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)
    result = service.list_my_documents(current_user)

    return success_response(
        data=[item.model_dump(mode="json") for item in result],
        message="OK",
        meta={
            "count": len(result),
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/{document_id}")
def get_my_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)

    result = service.get_my_document(
        user=current_user,
        document_id=document_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.delete("/{document_id}")
def delete_my_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)

    service.delete_my_document(
        user=current_user,
        document_id=document_id,
    )

    return success_response(
        data=None,
        message="Document deleted",
        meta={"trace_id": request.state.trace_id},
    )
