from sqlalchemy.orm import Session

from app.modules.consultants.models import ConsultProfile, ConsultRequest
from app.modules.orders.models import Order, OrderItem
from app.modules.rentals.models import LessorProfile, RentalRequest
from app.modules.reviews.models import MarketplaceReview
from app.modules.services.models import ServiceProviderProfile, ServiceRequest
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
