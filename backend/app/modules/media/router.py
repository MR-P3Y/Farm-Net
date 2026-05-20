from math import ceil

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.media.schemas import MediaUploadMetaIn
from app.modules.media.service import MediaService


router = APIRouter(
    prefix="/media",
    tags=["Media"],
)


@router.post("/upload")
async def upload_media(
    request: Request,
    file: UploadFile = File(...),
    purpose: str = Form(default="general"),
    visibility: str = Form(default="private"),
    alt_text: str | None = Form(default=None),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("media.upload")),
):
    if not file.filename:
        raise ValidationAuthError(
            message="Uploaded file must have a filename",
            details={"filename": "missing"},
        )

    content = await file.read()
    service = MediaService(db)

    result = service.store_uploaded_bytes(
        user=current_user,
        content=content,
        original_filename=file.filename,
        mime_type=file.content_type,
        meta=MediaUploadMetaIn(
            purpose=purpose,
            visibility=visibility,
            alt_text=alt_text,
            description=description,
        ),
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Media uploaded",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/me")
def list_my_media(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    purpose: str | None = Query(default=None),
    visibility: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("media.read")),
):
    service = MediaService(db)

    items, total = service.list_my_media(
        user=current_user,
        purpose=purpose,
        visibility=visibility,
        page=page,
        page_size=page_size,
    )

    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/{file_key}")
def get_my_media(
    file_key: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("media.read")),
):
    service = MediaService(db)

    result = service.get_my_media(user=current_user, file_key=file_key)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.delete("/{file_key}")
def delete_my_media(
    file_key: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("media.delete")),
):
    service = MediaService(db)

    result = service.delete_my_media(user=current_user, file_key=file_key)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Media deleted",
        meta={"trace_id": request.state.trace_id},
    )
