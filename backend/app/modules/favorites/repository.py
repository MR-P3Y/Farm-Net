from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.modules.consultants.enums import ConsultProfileStatus
from app.modules.consultants.models import ConsultProfile
from app.modules.favorites.enums import FavoriteSubjectType
from app.modules.favorites.models import UserFavorite
from app.modules.media.enums import MediaStatus, MediaVisibility
from app.modules.media.models import MediaFile
from app.modules.products.enums import ProductStatus
from app.modules.products.models import StoreProduct
from app.modules.rentals.enums import LessorStatus, RentalEquipmentStatus
from app.modules.rentals.models import LessorProfile, RentalEquipment
from app.modules.services.enums import ServiceOfferStatus, ServiceProviderStatus
from app.modules.services.models import ServiceOffer, ServiceProviderProfile
from app.modules.social.enums import SocialPostStatus, SocialPostVisibility
from app.modules.social.models import SocialBookmark, SocialPost
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store


class FavoritesRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_existing(
        self,
        *,
        user_id: int,
        subject_type: str,
        subject_id: int,
        for_update: bool = False,
    ) -> UserFavorite | None:
        query = self.db.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.subject_type == subject_type,
            UserFavorite.subject_id == subject_id,
        )
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def add(self, row: UserFavorite) -> UserFavorite:
        self.db.add(row)
        self.db.flush()
        return row

    def add_exact_once(self, row: UserFavorite) -> tuple[UserFavorite, bool]:
        try:
            with self.db.begin_nested():
                self.db.add(row)
                self.db.flush()
            return row, True
        except IntegrityError:
            existing = self.get_existing(
                user_id=row.user_id,
                subject_type=row.subject_type,
                subject_id=row.subject_id,
                for_update=True,
            )
            if existing is None:
                raise
            return existing, False

    def delete(self, row: UserFavorite) -> None:
        self.db.delete(row)
        self.db.flush()

    def list_own(
        self,
        *,
        user_id: int,
        subject_type: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[UserFavorite], int]:
        query = self.db.query(UserFavorite).filter(UserFavorite.user_id == user_id)
        if subject_type is not None:
            query = query.filter(UserFavorite.subject_type == subject_type)
        total = query.count()
        rows = (
            query.order_by(UserFavorite.created_at.desc(), UserFavorite.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def favorite_subject_ids(
        self,
        *,
        user_id: int,
        subject_type: str,
        subject_ids: list[int],
    ) -> list[int]:
        if not subject_ids:
            return []
        rows = (
            self.db.query(UserFavorite.subject_id)
            .filter(
                UserFavorite.user_id == user_id,
                UserFavorite.subject_type == subject_type,
                UserFavorite.subject_id.in_(subject_ids),
            )
            .order_by(UserFavorite.subject_id)
            .all()
        )
        return [int(row[0]) for row in rows]

    def public_subject(self, *, subject_type: str, subject_id: int):
        if subject_type == FavoriteSubjectType.PRODUCT.value:
            return (
                self.db.query(StoreProduct)
                .options(joinedload(StoreProduct.images), joinedload(StoreProduct.store))
                .filter(
                    StoreProduct.id == subject_id,
                    StoreProduct.status == ProductStatus.PUBLISHED.value,
                    StoreProduct.is_active.is_(True),
                    StoreProduct.deleted_at.is_(None),
                )
                .one_or_none()
            )
        if subject_type == FavoriteSubjectType.STORE.value:
            return (
                self.db.query(Store)
                .filter(
                    Store.id == subject_id,
                    Store.status == StoreStatus.APPROVED.value,
                    Store.deleted_at.is_(None),
                )
                .one_or_none()
            )
        if subject_type == FavoriteSubjectType.SERVICE_OFFER.value:
            return (
                self.db.query(ServiceOffer)
                .join(ServiceProviderProfile)
                .options(
                    joinedload(ServiceOffer.media),
                    joinedload(ServiceOffer.provider_profile),
                )
                .filter(
                    ServiceOffer.id == subject_id,
                    ServiceOffer.status == ServiceOfferStatus.APPROVED.value,
                    ServiceOffer.is_active.is_(True),
                    ServiceOffer.deleted_at.is_(None),
                    ServiceProviderProfile.status == ServiceProviderStatus.APPROVED.value,
                    ServiceProviderProfile.deleted_at.is_(None),
                )
                .one_or_none()
            )
        if subject_type == FavoriteSubjectType.RENTAL_EQUIPMENT.value:
            return (
                self.db.query(RentalEquipment)
                .join(LessorProfile)
                .options(
                    joinedload(RentalEquipment.media),
                    joinedload(RentalEquipment.lessor_profile),
                )
                .filter(
                    RentalEquipment.id == subject_id,
                    RentalEquipment.status == RentalEquipmentStatus.APPROVED.value,
                    RentalEquipment.is_active.is_(True),
                    RentalEquipment.deleted_at.is_(None),
                    LessorProfile.status == LessorStatus.APPROVED.value,
                    LessorProfile.deleted_at.is_(None),
                )
                .one_or_none()
            )
        if subject_type == FavoriteSubjectType.CONSULTANT.value:
            return (
                self.db.query(ConsultProfile)
                .filter(
                    ConsultProfile.id == subject_id,
                    ConsultProfile.status == ConsultProfileStatus.APPROVED.value,
                    ConsultProfile.deleted_at.is_(None),
                )
                .one_or_none()
            )
        return (
            self.db.query(SocialPost)
            .filter(
                SocialPost.id == subject_id,
                SocialPost.status == SocialPostStatus.PUBLISHED.value,
                SocialPost.visibility == SocialPostVisibility.PUBLIC.value,
                SocialPost.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def public_media_url(self, media_file_id: int | None) -> str | None:
        if media_file_id is None:
            return None
        file_key = (
            self.db.query(MediaFile.file_key)
            .filter(
                MediaFile.id == media_file_id,
                MediaFile.visibility == MediaVisibility.PUBLIC.value,
                MediaFile.status == MediaStatus.ACTIVE.value,
                MediaFile.deleted_at.is_(None),
            )
            .scalar()
        )
        return f"/api/v1/media/public/{file_key}" if file_key else None

    def sync_legacy_social_add(self, *, user_id: int, post_id: int) -> None:
        existing = (
            self.db.query(SocialBookmark)
            .filter(SocialBookmark.user_id == user_id, SocialBookmark.post_id == post_id)
            .one_or_none()
        )
        if existing is None:
            self.db.add(SocialBookmark(user_id=user_id, post_id=post_id))
            self.db.flush()

    def sync_legacy_social_delete(self, *, user_id: int, post_id: int) -> None:
        existing = (
            self.db.query(SocialBookmark)
            .filter(SocialBookmark.user_id == user_id, SocialBookmark.post_id == post_id)
            .one_or_none()
        )
        if existing is not None:
            self.db.delete(existing)
            self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
