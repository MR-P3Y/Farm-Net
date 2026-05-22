from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.media.service import MediaService


router = APIRouter(
    prefix="/admin/media",
    tags=["Admin Media Access"],
)


@router.get("/private/{file_key}")
def get_private_media_as_admin(
    file_key: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("media.admin_read")),
):
    service = MediaService(db)

    row, path = service.get_private_media_file_path(
        user=current_user,
        file_key=file_key,
        is_admin=True,
    )

    return FileResponse(
        path=path,
        media_type=row.mime_type,
        filename=row.original_filename,
        headers={
            "X-Trace-Id": request.state.trace_id,
            "Cache-Control": "private, no-store",
        },
    )
