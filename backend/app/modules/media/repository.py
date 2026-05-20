from sqlalchemy.orm import Session

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

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)
