from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.media.enums import MediaStatus
from app.modules.media.models import MediaFile
from app.modules.media.repository import MediaRepository
from app.modules.media.schemas import MediaFileOut, MediaUploadMetaIn
from app.modules.media.storage import LocalMediaStorage, get_local_media_storage


class MediaService:
    def __init__(
        self,
        db: Session,
        *,
        storage: LocalMediaStorage | None = None,
    ) -> None:
        self.db = db
        self.repo = MediaRepository(db)
        self.storage = storage or get_local_media_storage()

    def store_uploaded_bytes(
        self,
        *,
        user: AuthUser,
        content: bytes,
        original_filename: str,
        mime_type: str | None,
        meta: MediaUploadMetaIn,
    ) -> MediaFileOut:
        stored = self.storage.store_bytes(
            content=content,
            original_filename=original_filename,
            mime_type=mime_type,
            purpose=meta.purpose,
            visibility=meta.visibility,
        )

        try:
            row = self.repo.create_media_file(
                owner_user_id=user.id,
                file_key=stored.file_key,
                original_filename=stored.original_filename,
                stored_filename=stored.stored_filename,
                relative_path=stored.relative_path,
                storage_disk=stored.storage_disk,
                mime_type=stored.mime_type,
                extension=stored.extension,
                size_bytes=stored.size_bytes,
                checksum_sha256=stored.checksum_sha256,
                visibility=meta.visibility,
                status=MediaStatus.ACTIVE.value,
                purpose=meta.purpose,
                width=stored.width,
                height=stored.height,
                alt_text=meta.alt_text,
                description=meta.description,
            )
            self.repo.commit()
            self.repo.refresh(row)
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(
                message="Media file already exists",
                details={"file_key": stored.file_key},
            ) from exc

        return self._media_out(row)

    def _media_out(self, row: MediaFile) -> MediaFileOut:
        return MediaFileOut(
            id=row.id,
            owner_user_id=row.owner_user_id,
            file_key=row.file_key,
            original_filename=row.original_filename,
            stored_filename=row.stored_filename,
            relative_path=row.relative_path,
            storage_disk=row.storage_disk,
            mime_type=row.mime_type,
            extension=row.extension,
            size_bytes=row.size_bytes,
            checksum_sha256=row.checksum_sha256,
            visibility=row.visibility,
            status=row.status,
            purpose=row.purpose,
            width=row.width,
            height=row.height,
            alt_text=row.alt_text,
            description=row.description,
            created_at=row.created_at.isoformat(),
            updated_at=row.updated_at.isoformat(),
            deleted_at=row.deleted_at.isoformat() if row.deleted_at else None,
        )
