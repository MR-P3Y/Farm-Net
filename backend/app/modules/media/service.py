from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.media.enums import MediaPurpose, MediaStatus, MediaVisibility
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

    def list_my_media(
        self,
        *,
        user: AuthUser,
        purpose: str | None,
        visibility: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[MediaFileOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if purpose is not None:
            self._validate_purpose(purpose)

        if visibility is not None:
            self._validate_visibility(visibility)

        rows, total = self.repo.list_by_owner(
            owner_user_id=user.id,
            purpose=purpose,
            visibility=visibility,
            status=MediaStatus.ACTIVE.value,
            page=page,
            page_size=page_size,
        )

        return [self._media_out(row) for row in rows], total

    def get_my_media(
        self,
        *,
        user: AuthUser,
        file_key: str,
    ) -> MediaFileOut:
        row = self.repo.get_active_by_file_key_for_owner(
            file_key=file_key,
            owner_user_id=user.id,
        )

        if row is None:
            raise ValidationAuthError(
                message="Media file not found",
                details={"file_key": file_key},
            )

        return self._media_out(row)

    def delete_my_media(
        self,
        *,
        user: AuthUser,
        file_key: str,
    ) -> MediaFileOut:
        row = self.repo.get_active_by_file_key_for_owner(
            file_key=file_key,
            owner_user_id=user.id,
        )

        if row is None:
            raise ValidationAuthError(
                message="Media file not found",
                details={"file_key": file_key},
            )

        self.repo.soft_delete(media=row)
        self.repo.commit()
        self.repo.refresh(row)

        return self._media_out(row)

    def _validate_purpose(self, purpose: str) -> None:
        allowed = {item.value for item in MediaPurpose}

        if purpose not in allowed:
            raise ValidationAuthError(
                message="Invalid media purpose",
                details={"allowed": sorted(allowed)},
            )

    def _validate_visibility(self, visibility: str) -> None:
        allowed = {item.value for item in MediaVisibility}

        if visibility not in allowed:
            raise ValidationAuthError(
                message="Invalid media visibility",
                details={"allowed": sorted(allowed)},
            )

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
