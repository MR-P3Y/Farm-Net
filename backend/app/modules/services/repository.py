from __future__ import annotations

from decimal import Decimal

from sqlalchemy import case, or_, text
from sqlalchemy.orm import Session, joinedload

from app.common.money import CurrencyCode
from app.common.search import normalize_search_text
from app.common.search_sql import search_match_expression, search_relevance_expression

from app.modules.auth.models import AuthUser
from app.modules.media.models import MediaFile
from app.modules.profiles.models import UserProfile
from app.modules.services.enums import ServiceDiscoverySort
from app.modules.services.models import (
    ServiceCategory,
    ServiceOffer,
    ServiceOfferMedia,
    ServiceProviderCategory,
    ServiceProviderProfile,
    ServiceRequest,
    ServiceRequestStatusLog,
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

    def category_usage_counts(self, category_id: int) -> tuple[int, int, int, int]:
        children = self.db.query(ServiceCategory).filter(ServiceCategory.parent_id == category_id).count()
        provider_links = self.db.query(ServiceProviderCategory).filter(ServiceProviderCategory.category_id == category_id).count()
        offers = self.db.query(ServiceOffer).filter(ServiceOffer.category_id == category_id, ServiceOffer.deleted_at.is_(None)).count()
        requests = self.db.query(ServiceRequest).filter(ServiceRequest.category_id == category_id).count()
        return children, provider_links, offers, requests

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
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        sort: ServiceDiscoverySort | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ServiceOffer], int]:
        query = (
            self.db.query(ServiceOffer)
            .join(ServiceProviderProfile)
            .outerjoin(ServiceCategory, ServiceOffer.category_id == ServiceCategory.id)
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
            query = query.filter(ServiceOffer.category_id.in_(self._category_scope(category_id)))

        if provider_profile_id is not None:
            query = query.filter(ServiceOffer.provider_profile_id == provider_profile_id)

        if pricing_type:
            query = query.filter(ServiceOffer.pricing_type == pricing_type)

        if province_id is not None:
            query = query.filter(ServiceOffer.province_id == province_id)

        if city_id is not None:
            query = query.filter(ServiceOffer.city_id == city_id)

        normalized_q = normalize_search_text(q) if q else None
        if normalized_q:
            query = query.filter(
                search_match_expression(
                    normalized_q,
                    ServiceOffer.title,
                    ServiceOffer.slug,
                    ServiceOffer.short_description,
                    ServiceOffer.description,
                    ServiceOffer.service_area,
                    ServiceOffer.province_name,
                    ServiceOffer.city_name,
                    ServiceProviderProfile.display_name,
                    ServiceProviderProfile.title,
                    ServiceCategory.title,
                )
            )

        if min_price is not None:
            query = query.filter(
                ServiceOffer.currency == CurrencyCode.TOMAN.value,
                ServiceOffer.price_amount >= min_price,
            )

        if max_price is not None:
            query = query.filter(
                ServiceOffer.currency == CurrencyCode.TOMAN.value,
                ServiceOffer.price_amount <= max_price,
            )

        total = query.count()

        null_price = case((ServiceOffer.price_amount.is_(None), 1), else_=0)
        if sort == ServiceDiscoverySort.PRICE_ASC:
            ordering = (null_price.asc(), ServiceOffer.price_amount.asc(), ServiceOffer.id.desc())
        elif sort == ServiceDiscoverySort.PRICE_DESC:
            ordering = (null_price.asc(), ServiceOffer.price_amount.desc(), ServiceOffer.id.desc())
        elif sort == ServiceDiscoverySort.RATING:
            ordering = (
                ServiceProviderProfile.rating_average.desc(),
                ServiceProviderProfile.reviews_count.desc(),
                ServiceOffer.id.desc(),
            )
        elif sort == ServiceDiscoverySort.NEWEST:
            ordering = (ServiceOffer.created_at.desc(), ServiceOffer.id.desc())
        elif sort == ServiceDiscoverySort.RELEVANCE and normalized_q:
            ordering = (
                search_relevance_expression(
                    normalized_q,
                    ServiceOffer.title,
                    ServiceOffer.slug,
                    ServiceOffer.short_description,
                    ServiceOffer.description,
                    ServiceOffer.service_area,
                    ServiceProviderProfile.display_name,
                    ServiceProviderProfile.title,
                    ServiceCategory.title,
                ).desc(),
                ServiceOffer.is_featured.desc(),
                ServiceOffer.created_at.desc(),
                ServiceOffer.id.desc(),
            )
        else:
            ordering = (
                ServiceOffer.is_featured.desc(),
                ServiceOffer.created_at.desc(),
                ServiceOffer.id.desc(),
            )

        rows = (
            query.order_by(*ordering)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def _category_scope(self, category_id: int) -> set[int]:
        rows = self.db.query(ServiceCategory.id, ServiceCategory.parent_id).filter(
            ServiceCategory.is_active.is_(True)
        ).all()
        children: dict[int, list[int]] = {}
        known_ids = set()
        for row_id, parent_id in rows:
            known_ids.add(row_id)
            if parent_id is not None:
                children.setdefault(parent_id, []).append(row_id)
        if category_id not in known_ids:
            return {category_id}
        scope = {category_id}
        pending = [category_id]
        while pending:
            for child_id in children.get(pending.pop(), []):
                if child_id not in scope:
                    scope.add(child_id)
                    pending.append(child_id)
        return scope

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

    def add_request(self, row: ServiceRequest) -> ServiceRequest:
        self.db.add(row)
        self.db.flush()
        return row

    def get_request_by_id(self, request_id: int) -> ServiceRequest | None:
        return (
            self.db.query(ServiceRequest)
            .options(
                joinedload(ServiceRequest.offer),
                joinedload(ServiceRequest.category),
                joinedload(ServiceRequest.provider_profile),
                joinedload(ServiceRequest.status_logs),
            )
            .filter(
                ServiceRequest.id == request_id,
                ServiceRequest.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_requests(
        self,
        *,
        requester_user_id: int | None = None,
        provider_profile_id: int | None = None,
        provider_user_id: int | None = None,
        offer_id: int | None = None,
        category_id: int | None = None,
        province_id: int | None = None,
        city_id: int | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ServiceRequest], int]:
        query = (
            self.db.query(ServiceRequest)
            .options(
                joinedload(ServiceRequest.offer),
                joinedload(ServiceRequest.category),
                joinedload(ServiceRequest.provider_profile),
                joinedload(ServiceRequest.status_logs),
            )
            .filter(ServiceRequest.deleted_at.is_(None))
        )

        if requester_user_id is not None:
            query = query.filter(ServiceRequest.requester_user_id == requester_user_id)
        if provider_profile_id is not None:
            query = query.filter(ServiceRequest.provider_profile_id == provider_profile_id)
        if provider_user_id is not None:
            query = query.join(ServiceProviderProfile).filter(
                ServiceProviderProfile.user_id == provider_user_id
            )
        if offer_id is not None:
            query = query.filter(ServiceRequest.offer_id == offer_id)
        if category_id is not None:
            query = query.filter(ServiceRequest.category_id == category_id)
        if province_id is not None:
            query = query.filter(ServiceRequest.province_id == province_id)
        if city_id is not None:
            query = query.filter(ServiceRequest.city_id == city_id)
        if status is not None:
            query = query.filter(ServiceRequest.status == status)

        total = query.count()
        rows = (
            query.order_by(ServiceRequest.created_at.desc(), ServiceRequest.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def add_request_status_log(
        self,
        row: ServiceRequestStatusLog,
    ) -> ServiceRequestStatusLog:
        self.db.add(row)
        self.db.flush()
        return row

    def list_request_status_logs(self, request_id: int) -> list[ServiceRequestStatusLog]:
        return (
            self.db.query(ServiceRequestStatusLog)
            .filter(ServiceRequestStatusLog.request_id == request_id)
            .order_by(
                ServiceRequestStatusLog.created_at.asc(),
                ServiceRequestStatusLog.id.asc(),
            )
            .all()
        )

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, row) -> None:
        self.db.refresh(row)
