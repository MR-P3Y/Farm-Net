from __future__ import annotations

from sqlalchemy import or_, text
from sqlalchemy.orm import Session, joinedload

from app.modules.auth.models import AuthUser
from app.modules.media.models import MediaFile
from app.modules.profiles.models import UserProfile
from app.modules.services.models import (
    ServiceCategory,
    ServiceOffer,
    ServiceOfferMedia,
    ServiceProviderCategory,
    ServiceProviderProfile,
)


class ServicesRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_category(self, row: ServiceCategory) -> ServiceCategory:
        self.db.add(row)
        self.db.flush()
        return row

    def get_category_by_id(self, category_id: int) -> ServiceCategory | None:
        return (
            self.db.query(ServiceCategory)
            .filter(ServiceCategory.id == category_id)
            .one_or_none()
        )

    def get_category_by_code(self, code: str) -> ServiceCategory | None:
        return (
            self.db.query(ServiceCategory)
            .filter(ServiceCategory.code == code)
            .one_or_none()
        )

    def list_categories(
        self,
        *,
        active_only: bool = False,
        q: str | None = None,
    ) -> list[ServiceCategory]:
        query = self.db.query(ServiceCategory)

        if active_only:
            query = query.filter(ServiceCategory.is_active.is_(True))

        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    ServiceCategory.code.ilike(like),
                    ServiceCategory.title.ilike(like),
                    ServiceCategory.description.ilike(like),
                )
            )

        return (
            query.order_by(
                ServiceCategory.sort_order.asc(),
                ServiceCategory.title.asc(),
                ServiceCategory.id.asc(),
            )
            .all()
        )

    def add_profile(self, row: ServiceProviderProfile) -> ServiceProviderProfile:
        self.db.add(row)
        self.db.flush()
        return row

    def get_profile_by_id(self, profile_id: int) -> ServiceProviderProfile | None:
        return (
            self.db.query(ServiceProviderProfile)
            .options(
                joinedload(ServiceProviderProfile.category_links).joinedload(
                    ServiceProviderCategory.category
                )
            )
            .filter(ServiceProviderProfile.id == profile_id)
            .one_or_none()
        )

    def get_profile_by_user_id(self, user_id: int) -> ServiceProviderProfile | None:
        return (
            self.db.query(ServiceProviderProfile)
            .options(
                joinedload(ServiceProviderProfile.category_links).joinedload(
                    ServiceProviderCategory.category
                )
            )
            .filter(
                ServiceProviderProfile.user_id == user_id,
                ServiceProviderProfile.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_profiles(
        self,
        *,
        status: str | None = None,
        category_id: int | None = None,
        q: str | None = None,
        province_id: int | None = None,
        city_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ServiceProviderProfile], int]:
        query = (
            self.db.query(ServiceProviderProfile)
            .options(
                joinedload(ServiceProviderProfile.category_links).joinedload(
                    ServiceProviderCategory.category
                )
            )
            .filter(ServiceProviderProfile.deleted_at.is_(None))
        )

        if status:
            query = query.filter(ServiceProviderProfile.status == status)

        if province_id is not None:
            query = query.filter(ServiceProviderProfile.province_id == province_id)

        if city_id is not None:
            query = query.filter(ServiceProviderProfile.city_id == city_id)

        if category_id is not None:
            query = query.join(ServiceProviderCategory).filter(
                ServiceProviderCategory.category_id == category_id
            )

        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    ServiceProviderProfile.display_name.ilike(like),
                    ServiceProviderProfile.title.ilike(like),
                    ServiceProviderProfile.bio.ilike(like),
                    ServiceProviderProfile.province_name.ilike(like),
                    ServiceProviderProfile.city_name.ilike(like),
                    ServiceProviderProfile.service_area.ilike(like),
                )
            )

        total = query.count()

        rows = (
            query.order_by(
                ServiceProviderProfile.is_featured.desc(),
                ServiceProviderProfile.rating_average.desc(),
                ServiceProviderProfile.reviews_count.desc(),
                ServiceProviderProfile.created_at.desc(),
                ServiceProviderProfile.id.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def replace_profile_categories(
        self,
        *,
        profile: ServiceProviderProfile,
        category_ids: list[int],
    ) -> None:
        existing = {
            link.category_id: link
            for link in self.db.query(ServiceProviderCategory)
            .filter(ServiceProviderCategory.provider_profile_id == profile.id)
            .all()
        }
        wanted = set(category_ids)

        for category_id, link in existing.items():
            if category_id not in wanted:
                self.db.delete(link)

        for category_id in wanted:
            if category_id not in existing:
                self.db.add(
                    ServiceProviderCategory(
                        provider_profile_id=profile.id,
                        category_id=category_id,
                    )
                )

        self.db.flush()

    def add_offer(self, row: ServiceOffer) -> ServiceOffer:
        self.db.add(row)
        self.db.flush()
        return row

    def get_offer_by_id(self, offer_id: int) -> ServiceOffer | None:
        return (
            self.db.query(ServiceOffer)
            .options(
                joinedload(ServiceOffer.category),
                joinedload(ServiceOffer.media),
                joinedload(ServiceOffer.provider_profile).joinedload(
                    ServiceProviderProfile.category_links
                ).joinedload(ServiceProviderCategory.category),
            )
            .filter(ServiceOffer.id == offer_id)
            .one_or_none()
        )

    def get_public_offer_by_id(self, offer_id: int) -> ServiceOffer | None:
        return (
            self.db.query(ServiceOffer)
            .join(ServiceProviderProfile)
            .options(
                joinedload(ServiceOffer.category),
                joinedload(ServiceOffer.media),
                joinedload(ServiceOffer.provider_profile).joinedload(
                    ServiceProviderProfile.category_links
                ).joinedload(ServiceProviderCategory.category),
            )
            .filter(
                ServiceOffer.id == offer_id,
                ServiceOffer.status == "approved",
                ServiceOffer.is_active.is_(True),
                ServiceOffer.deleted_at.is_(None),
                ServiceProviderProfile.status == "approved",
                ServiceProviderProfile.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_public_offers(
        self,
        *,
        category_id: int | None = None,
        provider_profile_id: int | None = None,
        pricing_type: str | None = None,
        q: str | None = None,
        province_id: int | None = None,
        city_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ServiceOffer], int]:
        query = (
            self.db.query(ServiceOffer)
            .join(ServiceProviderProfile)
            .options(
                joinedload(ServiceOffer.category),
                joinedload(ServiceOffer.media),
                joinedload(ServiceOffer.provider_profile).joinedload(
                    ServiceProviderProfile.category_links
                ).joinedload(ServiceProviderCategory.category),
            )
            .filter(
                ServiceOffer.status == "approved",
                ServiceOffer.is_active.is_(True),
                ServiceOffer.deleted_at.is_(None),
                ServiceProviderProfile.status == "approved",
                ServiceProviderProfile.deleted_at.is_(None),
            )
        )

        if category_id is not None:
            query = query.filter(ServiceOffer.category_id == category_id)

        if provider_profile_id is not None:
            query = query.filter(ServiceOffer.provider_profile_id == provider_profile_id)

        if pricing_type:
            query = query.filter(ServiceOffer.pricing_type == pricing_type)

        if province_id is not None:
            query = query.filter(ServiceOffer.province_id == province_id)

        if city_id is not None:
            query = query.filter(ServiceOffer.city_id == city_id)

        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    ServiceOffer.title.ilike(like),
                    ServiceOffer.slug.ilike(like),
                    ServiceOffer.short_description.ilike(like),
                    ServiceOffer.description.ilike(like),
                    ServiceOffer.service_area.ilike(like),
                    ServiceOffer.province_name.ilike(like),
                    ServiceOffer.city_name.ilike(like),
                )
            )

        total = query.count()

        rows = (
            query.order_by(
                ServiceOffer.is_featured.desc(),
                ServiceOffer.created_at.desc(),
                ServiceOffer.id.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def list_provider_offers(
        self,
        *,
        provider_profile_id: int,
        status: str | None = None,
        category_id: int | None = None,
        q: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ServiceOffer], int]:
        query = (
            self.db.query(ServiceOffer)
            .options(
                joinedload(ServiceOffer.category),
                joinedload(ServiceOffer.media),
                joinedload(ServiceOffer.provider_profile).joinedload(
                    ServiceProviderProfile.category_links
                ).joinedload(ServiceProviderCategory.category),
            )
            .filter(
                ServiceOffer.provider_profile_id == provider_profile_id,
                ServiceOffer.deleted_at.is_(None),
            )
        )

        if status:
            query = query.filter(ServiceOffer.status == status)

        if category_id is not None:
            query = query.filter(ServiceOffer.category_id == category_id)

        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    ServiceOffer.title.ilike(like),
                    ServiceOffer.short_description.ilike(like),
                    ServiceOffer.description.ilike(like),
                    ServiceOffer.service_area.ilike(like),
                )
            )

        total = query.count()

        rows = (
            query.order_by(ServiceOffer.created_at.desc(), ServiceOffer.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def list_admin_offers(
        self,
        *,
        status: str | None = None,
        category_id: int | None = None,
        provider_profile_id: int | None = None,
        pricing_type: str | None = None,
        q: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ServiceOffer], int]:
        query = (
            self.db.query(ServiceOffer)
            .options(
                joinedload(ServiceOffer.category),
                joinedload(ServiceOffer.media),
                joinedload(ServiceOffer.provider_profile).joinedload(
                    ServiceProviderProfile.category_links
                ).joinedload(ServiceProviderCategory.category),
            )
            .filter(ServiceOffer.deleted_at.is_(None))
        )

        if status:
            query = query.filter(ServiceOffer.status == status)

        if category_id is not None:
            query = query.filter(ServiceOffer.category_id == category_id)

        if provider_profile_id is not None:
            query = query.filter(ServiceOffer.provider_profile_id == provider_profile_id)

        if pricing_type:
            query = query.filter(ServiceOffer.pricing_type == pricing_type)

        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    ServiceOffer.title.ilike(like),
                    ServiceOffer.slug.ilike(like),
                    ServiceOffer.short_description.ilike(like),
                    ServiceOffer.description.ilike(like),
                    ServiceOffer.service_area.ilike(like),
                )
            )

        total = query.count()

        rows = (
            query.order_by(ServiceOffer.created_at.desc(), ServiceOffer.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def replace_offer_media(
        self,
        *,
        offer: ServiceOffer,
        rows: list[ServiceOfferMedia],
    ) -> None:
        for existing in list(offer.media):
            self.db.delete(existing)

        self.db.flush()

        for row in rows:
            row.offer_id = offer.id
            self.db.add(row)

        self.db.flush()

    def get_user_by_id(self, user_id: int) -> AuthUser | None:
        return self.db.query(AuthUser).filter(AuthUser.id == user_id).one_or_none()

    def get_user_profile(self, user_id: int) -> UserProfile | None:
        return (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .one_or_none()
        )

    def get_media_file_by_id(self, media_file_id: int) -> MediaFile | None:
        return self.db.query(MediaFile).filter(MediaFile.id == media_file_id).one_or_none()

    def list_service_admin_recipient_user_ids(self) -> list[int]:
        rows = self.db.execute(
            text(
                """
                SELECT DISTINCT u.id
                FROM auth_users u
                JOIN auth_user_roles ur ON ur.user_id = u.id
                JOIN auth_roles r ON r.id = ur.role_id
                WHERE r.code IN ('admin', 'super_admin', 'verification_admin', 'content_manager')
                ORDER BY u.id
                """
            )
        ).fetchall()

        return [int(row[0]) for row in rows]

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, row) -> None:
        self.db.refresh(row)
