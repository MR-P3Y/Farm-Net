from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserFavorite(Base):
    __tablename__ = "user_favorites"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "subject_type",
            "subject_id",
            name="uq_user_favorites_owner_subject",
        ),
        CheckConstraint(
            "subject_id > 0",
            name="ck_user_favorites_subject_id_positive",
        ),
        CheckConstraint(
            "subject_type IN "
            "('product', 'store', 'service_offer', 'rental_equipment', "
            "'consultant', 'social_post')",
            name="ck_user_favorites_subject_type",
        ),
        Index(
            "ix_user_favorites_owner_created",
            "user_id",
            "created_at",
            "id",
        ),
        Index(
            "ix_user_favorites_subject",
            "subject_type",
            "subject_id",
        ),
    )
