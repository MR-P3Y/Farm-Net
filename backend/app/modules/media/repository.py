from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.media.enums import MediaStatus
from app.modules.media.models import MediaFile


class MediaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_media_file(
        self,
        *,
        owner_user_id: int | None,
        file_key: str,
        original_filename: str,
        stored_filename: str,
        relative_path: str,
        storage_disk: str,
        mime_type: str,
        extension: str,
        size_bytes: int,
        checksum_sha256: str,
        visibility: str,
        status: str,
        purpose: str,
        width: int | None,
        height: int | None,
        alt_text: str | None,
        description: str | None,
    ) -> MediaFile:
        row = MediaFile(
            owner_user_id=owner_user_id,
            file_key=file_key,
            original_filename=original_filename,
            stored_filename=stored_filename,
            relative_path=relative_path,
            storage_disk=storage_disk,
            mime_type=mime_type,
            extension=extension,
            size_bytes=size_bytes,
            checksum_sha256=checksum_sha256,
            visibility=visibility,
            status=status,
            purpose=purpose,
            width=width,
            height=height,
            alt_text=alt_text,
            description=description,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_by_file_key(self, *, file_key: str) -> MediaFile | None:
        return (
            self.db.query(MediaFile)
            .filter(MediaFile.file_key == file_key)
            .one_or_none()
        )

    def get_by_id(self, *, media_id: int) -> MediaFile | None:
        return self.db.query(MediaFile).filter(MediaFile.id == media_id).one_or_none()

    def list_by_owner(
        self,
        *,
        owner_user_id: int,
        purpose: str | None = None,
        visibility: str | None = None,
        status: str = MediaStatus.ACTIVE.value,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[MediaFile], int]:
        query = self.db.query(MediaFile).filter(
            MediaFile.owner_user_id == owner_user_id,
            MediaFile.status == status,
        )

        if purpose:
            query = query.filter(MediaFile.purpose == purpose)

        if visibility:
            query = query.filter(MediaFile.visibility == visibility)

        total = query.count()

        items = (
            query.order_by(MediaFile.created_at.desc(), MediaFile.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def get_active_by_file_key_for_owner(
        self,
        *,
        file_key: str,
        owner_user_id: int,
    ) -> MediaFile | None:
        return (
            self.db.query(MediaFile)
            .filter(
                MediaFile.file_key == file_key,
                MediaFile.owner_user_id == owner_user_id,
                MediaFile.status == MediaStatus.ACTIVE.value,
            )
            .one_or_none()
        )

    def soft_delete(self, *, media: MediaFile) -> None:
        media.status = MediaStatus.DELETED.value
        media.deleted_at = datetime.utcnow()
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)
