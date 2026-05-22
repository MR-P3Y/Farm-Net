from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.modules.media.enums import (
    MediaPurpose,
    MediaStatus,
    MediaStorageDisk,
    MediaVisibility,
)


class MediaFile(Base):
    __tablename__ = "media_files"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    owner_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    file_key: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    relative_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    storage_disk: Mapped[str] = mapped_column(
        String(50),
        default=MediaStorageDisk.LOCAL.value,
        nullable=False,
        index=True,
    )

    mime_type: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )

    extension: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    checksum_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    visibility: Mapped[str] = mapped_column(
        String(30),
        default=MediaVisibility.PRIVATE.value,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default=MediaStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )

    purpose: Mapped[str] = mapped_column(
        String(80),
        default=MediaPurpose.GENERAL.value,
        nullable=False,
        index=True,
    )

    width: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    height: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    alt_text: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "storage_disk",
            "relative_path",
            name="uq_media_files_disk_relative_path",
        ),
        Index(
            "ix_media_files_owner_status",
            "owner_user_id",
            "status",
        ),
        Index(
            "ix_media_files_purpose_visibility_status",
            "purpose",
            "visibility",
            "status",
        ),
        Index(
            "ix_media_files_created",
            "created_at",
        ),
    )