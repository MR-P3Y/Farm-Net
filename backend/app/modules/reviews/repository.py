from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from decimal import Decimal

from app.modules.consultants.enums import ConsultProfileStatus
from app.modules.consultants.models import ConsultProfile, ConsultRequest
from app.modules.orders.models import Order, OrderItem
from app.modules.products.enums import ProductStatus
from app.modules.products.models import StoreProduct
from app.modules.profiles.models import UserProfile
from app.modules.rentals.enums import LessorStatus, RentalEquipmentStatus
from app.modules.rentals.models import LessorProfile, RentalEquipment, RentalRequest
from app.modules.reviews.enums import ReviewSubjectType
from app.modules.reviews.models import (
    MarketplaceRatingAggregate,
    MarketplaceReview,
    MarketplaceReviewModerationLog,
    MarketplaceReviewReport,
)
from app.modules.services.enums import ServiceOfferStatus, ServiceProviderStatus
from app.modules.services.models import (
    ServiceOffer,
    ServiceProviderProfile,
    ServiceRequest,
)
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store


class ReviewsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_order_for_update(self, source_id: int) -> Order | None:
        return (
            self.db.query(Order)
            .filter(Order.id == source_id, Order.deleted_at.is_(None))
            .with_for_update()
            .one_or_none()
        )

    def order_has_product(self, *, order_id: int, product_id: int) -> bool:
        return (
            self.db.query(OrderItem.id)
            .filter(
                OrderItem.order_id == order_id,
                OrderItem.product_id == product_id,
            )
            .first()
            is not None
        )

    def get_store(self, store_id: int) -> Store | None:
        return (
            self.db.query(Store)
            .filter(Store.id == store_id, Store.deleted_at.is_(None))
            .one_or_none()
        )

    def get_service_request_for_update(self, source_id: int) -> ServiceRequest | None:
        return (
            self.db.query(ServiceRequest)
            .filter(
                ServiceRequest.id == source_id,
                ServiceRequest.deleted_at.is_(None),
            )
            .with_for_update()
            .one_or_none()
        )

    def get_service_provider(self, profile_id: int) -> ServiceProviderProfile | None:
        return (
            self.db.query(ServiceProviderProfile)
            .filter(
                ServiceProviderProfile.id == profile_id,
                ServiceProviderProfile.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def get_rental_request_for_update(self, source_id: int) -> RentalRequest | None:
        return (
            self.db.query(RentalRequest)
            .filter(RentalRequest.id == source_id)
            .with_for_update()
            .one_or_none()
        )

    def get_lessor_profile(self, profile_id: int) -> LessorProfile | None:
        return (
            self.db.query(LessorProfile)
            .filter(
                LessorProfile.id == profile_id,
                LessorProfile.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def get_consult_request_for_update(self, source_id: int) -> ConsultRequest | None:
        return (
            self.db.query(ConsultRequest)
            .filter(
                ConsultRequest.id == source_id,
                ConsultRequest.deleted_at.is_(None),
            )
            .with_for_update()
            .one_or_none()
        )

    def get_consultant_profile(self, profile_id: int) -> ConsultProfile | None:
        return (
            self.db.query(ConsultProfile)
            .filter(
                ConsultProfile.id == profile_id,
                ConsultProfile.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def get_existing(
        self,
        *,
        reviewer_user_id: int,
        source_type: str,
        source_id: int,
        subject_type: str,
        subject_id: int,
    ) -> MarketplaceReview | None:
        return (
            self.db.query(MarketplaceReview)
            .filter(
                MarketplaceReview.reviewer_user_id == reviewer_user_id,
                MarketplaceReview.source_type == source_type,
                MarketplaceReview.source_id == source_id,
                MarketplaceReview.subject_type == subject_type,
                MarketplaceReview.subject_id == subject_id,
            )
            .one_or_none()
        )

    def add(self, row: MarketplaceReview) -> MarketplaceReview:
        self.db.add(row)
        self.db.flush()
        return row

    def get_aggregate(
        self,
        *,
        subject_type: str,
        subject_id: int,
        for_update: bool = False,
    ) -> MarketplaceRatingAggregate | None:
        query = self.db.query(MarketplaceRatingAggregate).filter(
            MarketplaceRatingAggregate.subject_type == subject_type,
            MarketplaceRatingAggregate.subject_id == subject_id,
        )
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def rating_values(
        self, *, subject_type: str, subject_id: int
    ) -> tuple[Decimal, int]:
        aggregate = self.get_aggregate(
            subject_type=subject_type,
            subject_id=subject_id,
        )
        if aggregate is None:
            return Decimal("0.00"), 0
        return aggregate.rating_average, aggregate.reviews_count

    def add_aggregate(
        self, row: MarketplaceRatingAggregate
    ) -> MarketplaceRatingAggregate:
        self.db.add(row)
        self.db.flush()
        return row

    def get_or_create_aggregate(
        self, *, subject_type: str, subject_id: int
    ) -> MarketplaceRatingAggregate:
        existing = self.get_aggregate(
            subject_type=subject_type,
            subject_id=subject_id,
            for_update=True,
        )
        if existing is not None:
            return existing
        candidate = MarketplaceRatingAggregate(
            subject_type=subject_type,
            subject_id=subject_id,
            rating_sum=0,
            reviews_count=0,
            rating_average=Decimal("0.00"),
        )
        try:
            with self.db.begin_nested():
                self.db.add(candidate)
                self.db.flush()
            return candidate
        except IntegrityError:
            existing = self.get_aggregate(
                subject_type=subject_type,
                subject_id=subject_id,
                for_update=True,
            )
            if existing is None:
                raise
            return existing

    def sync_legacy_rating_projection(
        self,
        *,
        subject_type: str,
        subject_id: int,
        rating_average,
        reviews_count: int,
    ) -> None:
        if subject_type == ReviewSubjectType.SERVICE_PROVIDER.value:
            self.db.query(ServiceProviderProfile).filter(
                ServiceProviderProfile.id == subject_id
            ).update(
                {
                    ServiceProviderProfile.rating_average: rating_average,
                    ServiceProviderProfile.reviews_count: reviews_count,
                },
                synchronize_session=False,
            )
        elif subject_type == ReviewSubjectType.CONSULTANT.value:
            self.db.query(ConsultProfile).filter(
                ConsultProfile.id == subject_id
            ).update(
                {
                    ConsultProfile.rating_average: rating_average,
                    ConsultProfile.reviews_count: reviews_count,
                },
                synchronize_session=False,
            )

    def list_public(
        self,
        *,
        subject_type: str,
        subject_id: int,
        page: int,
        page_size: int,
    ) -> tuple[list[tuple[MarketplaceReview, UserProfile | None]], int]:
        query = (
            self.db.query(MarketplaceReview, UserProfile)
            .outerjoin(
                UserProfile,
                UserProfile.user_id == MarketplaceReview.reviewer_user_id,
            )
            .filter(
                MarketplaceReview.subject_type == subject_type,
                MarketplaceReview.subject_id == subject_id,
                MarketplaceReview.status == "active",
            )
        )
        total = query.count()
        rows = (
            query.order_by(
                MarketplaceReview.created_at.desc(),
                MarketplaceReview.id.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def public_subject_exists(self, *, subject_type: str, subject_id: int) -> bool:
        if subject_type == ReviewSubjectType.PRODUCT.value:
            query = self.db.query(StoreProduct.id).filter(
                StoreProduct.id == subject_id,
                StoreProduct.status == ProductStatus.PUBLISHED.value,
                StoreProduct.deleted_at.is_(None),
            )
        elif subject_type == ReviewSubjectType.STORE.value:
            query = self.db.query(Store.id).filter(
                Store.id == subject_id,
                Store.status == StoreStatus.APPROVED.value,
                Store.deleted_at.is_(None),
            )
        elif subject_type == ReviewSubjectType.SERVICE_OFFER.value:
            query = self.db.query(ServiceOffer.id).filter(
                ServiceOffer.id == subject_id,
                ServiceOffer.status == ServiceOfferStatus.APPROVED.value,
                ServiceOffer.is_active.is_(True),
                ServiceOffer.deleted_at.is_(None),
            )
        elif subject_type == ReviewSubjectType.SERVICE_PROVIDER.value:
            query = self.db.query(ServiceProviderProfile.id).filter(
                ServiceProviderProfile.id == subject_id,
                ServiceProviderProfile.status == ServiceProviderStatus.APPROVED.value,
                ServiceProviderProfile.deleted_at.is_(None),
            )
        elif subject_type == ReviewSubjectType.RENTAL_EQUIPMENT.value:
            query = self.db.query(RentalEquipment.id).filter(
                RentalEquipment.id == subject_id,
                RentalEquipment.status == RentalEquipmentStatus.APPROVED.value,
                RentalEquipment.is_active.is_(True),
                RentalEquipment.deleted_at.is_(None),
            )
        elif subject_type == ReviewSubjectType.RENTAL_LESSOR.value:
            query = self.db.query(LessorProfile.id).filter(
                LessorProfile.id == subject_id,
                LessorProfile.status == LessorStatus.APPROVED.value,
                LessorProfile.deleted_at.is_(None),
            )
        else:
            query = self.db.query(ConsultProfile.id).filter(
                ConsultProfile.id == subject_id,
                ConsultProfile.status == ConsultProfileStatus.APPROVED.value,
                ConsultProfile.deleted_at.is_(None),
            )
        return query.first() is not None

    def get_review(self, review_id: int, *, for_update: bool = False):
        query = self.db.query(MarketplaceReview).filter(
            MarketplaceReview.id == review_id
        )
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def get_report_by_reporter(self, *, review_id: int, reporter_user_id: int):
        return (
            self.db.query(MarketplaceReviewReport)
            .filter(
                MarketplaceReviewReport.review_id == review_id,
                MarketplaceReviewReport.reporter_user_id == reporter_user_id,
            )
            .one_or_none()
        )

    def add_report(self, row: MarketplaceReviewReport):
        self.db.add(row)
        self.db.flush()
        return row

    def list_admin_reviews(
        self, *, status: str | None, page: int, page_size: int
    ):
        query = self.db.query(MarketplaceReview)
        if status is not None:
            query = query.filter(MarketplaceReview.status == status)
        total = query.count()
        return (
            query.order_by(MarketplaceReview.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all(),
            total,
        )

    def list_admin_reports(
        self, *, status: str | None, page: int, page_size: int
    ):
        query = self.db.query(MarketplaceReviewReport)
        if status is not None:
            query = query.filter(MarketplaceReviewReport.status == status)
        total = query.count()
        return (
            query.order_by(MarketplaceReviewReport.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all(),
            total,
        )

    def get_report(self, report_id: int, *, for_update: bool = False):
        query = self.db.query(MarketplaceReviewReport).filter(
            MarketplaceReviewReport.id == report_id
        )
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def add_moderation_log(self, row: MarketplaceReviewModerationLog):
        self.db.add(row)
        self.db.flush()
        return row

    def list_moderation_logs(self, review_id: int):
        return (
            self.db.query(MarketplaceReviewModerationLog)
            .filter(MarketplaceReviewModerationLog.review_id == review_id)
            .order_by(MarketplaceReviewModerationLog.created_at, MarketplaceReviewModerationLog.id)
            .all()
        )

    def list_recipient_user_ids_for_permission(self, permission_code: str) -> list[int]:
        rows = self.db.execute(
            text(
                """
                SELECT DISTINCT u.id
                FROM auth_users u
                JOIN auth_user_roles ur ON ur.user_id = u.id
                JOIN auth_roles r ON r.id = ur.role_id AND r.is_active = 1
                JOIN auth_role_permissions rp ON rp.role_id = r.id
                JOIN auth_permissions p
                  ON p.id = rp.permission_id AND p.is_active = 1
                WHERE p.code = :permission_code AND u.status = 'active'
                ORDER BY u.id
                """
            ),
            {"permission_code": permission_code},
        ).fetchall()
        return [int(row[0]) for row in rows]

    def list_own(
        self,
        *,
        reviewer_user_id: int,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[MarketplaceReview], int]:
        query = self.db.query(MarketplaceReview).filter(
            MarketplaceReview.reviewer_user_id == reviewer_user_id
        )
        if status is not None:
            query = query.filter(MarketplaceReview.status == status)
        total = query.count()
        rows = (
            query.order_by(
                MarketplaceReview.created_at.desc(),
                MarketplaceReview.id.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def get_own(
        self,
        *,
        review_id: int,
        reviewer_user_id: int,
        for_update: bool = False,
    ) -> MarketplaceReview | None:
        query = self.db.query(MarketplaceReview).filter(
            MarketplaceReview.id == review_id,
            MarketplaceReview.reviewer_user_id == reviewer_user_id,
        )
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
