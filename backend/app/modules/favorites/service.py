from app.modules.favorites.enums import FavoriteSubjectType
from app.modules.favorites.exceptions import FavoriteSubjectNotFoundError
from app.modules.favorites.models import UserFavorite
from app.modules.favorites.repository import FavoritesRepository
from app.modules.favorites.schemas import FavoriteItemOut, FavoriteStatusOut


class FavoritesService:
    def __init__(self, db, repository: FavoritesRepository | None = None) -> None:
        self.repo = repository or FavoritesRepository(db)

    def add(
        self,
        *,
        user_id: int,
        subject_type: FavoriteSubjectType,
        subject_id: int,
    ) -> tuple[FavoriteItemOut, bool]:
        subject = self.repo.public_subject(
            subject_type=subject_type.value,
            subject_id=subject_id,
        )
        if subject is None:
            raise FavoriteSubjectNotFoundError()

        existing = self.repo.get_existing(
            user_id=user_id,
            subject_type=subject_type.value,
            subject_id=subject_id,
            for_update=True,
        )
        created = False
        if existing is None:
            existing, created = self.repo.add_exact_once(
                UserFavorite(
                    user_id=user_id,
                    subject_type=subject_type.value,
                    subject_id=subject_id,
                )
            )

        if subject_type == FavoriteSubjectType.SOCIAL_POST:
            self.repo.sync_legacy_social_add(user_id=user_id, post_id=subject_id)
        self.repo.commit()
        return self._out(existing, subject=subject), created

    def remove(
        self,
        *,
        user_id: int,
        subject_type: FavoriteSubjectType,
        subject_id: int,
    ) -> bool:
        existing = self.repo.get_existing(
            user_id=user_id,
            subject_type=subject_type.value,
            subject_id=subject_id,
            for_update=True,
        )
        removed = existing is not None
        if existing is not None:
            self.repo.delete(existing)
        if subject_type == FavoriteSubjectType.SOCIAL_POST:
            self.repo.sync_legacy_social_delete(user_id=user_id, post_id=subject_id)
        self.repo.commit()
        return removed

    def list_own(
        self,
        *,
        user_id: int,
        subject_type: FavoriteSubjectType | None,
        page: int,
        page_size: int,
    ) -> tuple[list[FavoriteItemOut], int]:
        rows, total = self.repo.list_own(
            user_id=user_id,
            subject_type=subject_type.value if subject_type else None,
            page=page,
            page_size=page_size,
        )
        items = []
        for row in rows:
            subject = self.repo.public_subject(
                subject_type=row.subject_type,
                subject_id=row.subject_id,
            )
            items.append(self._out(row, subject=subject))
        return items, total

    def status(
        self,
        *,
        user_id: int,
        subject_type: FavoriteSubjectType,
        subject_ids: list[int],
    ) -> FavoriteStatusOut:
        unique_ids = sorted(set(subject_ids))
        return FavoriteStatusOut(
            subject_type=subject_type,
            favorite_subject_ids=self.repo.favorite_subject_ids(
                user_id=user_id,
                subject_type=subject_type.value,
                subject_ids=unique_ids,
            ),
        )

    def _out(self, row: UserFavorite, *, subject) -> FavoriteItemOut:
        if subject is None:
            return FavoriteItemOut(
                id=row.id,
                subject_type=FavoriteSubjectType(row.subject_type),
                subject_id=row.subject_id,
                is_available=False,
                created_at=row.created_at,
            )

        title, subtitle, image_url, route = self._subject_snapshot(
            FavoriteSubjectType(row.subject_type), subject
        )
        return FavoriteItemOut(
            id=row.id,
            subject_type=FavoriteSubjectType(row.subject_type),
            subject_id=row.subject_id,
            title=title,
            subtitle=subtitle,
            image_url=image_url,
            route=route,
            is_available=True,
            created_at=row.created_at,
        )

    def _subject_snapshot(self, subject_type: FavoriteSubjectType, subject):
        if subject_type == FavoriteSubjectType.PRODUCT:
            image = next(
                (item for item in subject.images if item.is_primary),
                subject.images[0] if subject.images else None,
            )
            return (
                subject.name,
                subject.short_description or getattr(subject.store, "name", None),
                self.repo.public_media_url(image.media_file_id if image else None),
                f"/products/{subject.id}",
            )
        if subject_type == FavoriteSubjectType.STORE:
            return (
                subject.name,
                subject.description,
                self.repo.public_media_url(subject.logo_media_file_id),
                f"/stores/{subject.slug}",
            )
        if subject_type == FavoriteSubjectType.SERVICE_OFFER:
            media = next(
                (item for item in subject.media if item.is_primary),
                subject.media[0] if subject.media else None,
            )
            return (
                subject.title,
                subject.short_description or subject.service_area,
                self.repo.public_media_url(media.media_file_id if media else None),
                f"/services/{subject.id}",
            )
        if subject_type == FavoriteSubjectType.RENTAL_EQUIPMENT:
            media = next(
                (item for item in subject.media if item.is_primary),
                subject.media[0] if subject.media else None,
            )
            subtitle = " ".join(
                item for item in [subject.manufacturer, subject.model_name] if item
            ) or getattr(subject.lessor_profile, "display_name", None)
            return (
                subject.title,
                subtitle,
                self.repo.public_media_url(media.media_file_id if media else None),
                f"/rentals/equipment/{subject.id}",
            )
        if subject_type == FavoriteSubjectType.CONSULTANT:
            return (
                subject.display_name or subject.title or "Consultant",
                subject.title,
                self.repo.public_media_url(subject.avatar_media_file_id),
                f"/consultants/{subject.id}",
            )
        return (
            subject.title,
            subject.body[:500],
            self.repo.public_media_url(subject.media_file_id),
            f"/social/detail/{subject.id}",
        )
