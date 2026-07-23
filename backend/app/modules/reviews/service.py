from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import PermissionDeniedError
from app.modules.auth.models import AuthUser
from app.modules.consultants.enums import ConsultRequestStatus
from app.modules.orders.enums import OrderStatus
from app.modules.rentals.enums import RentalRequestStatus
from app.modules.reviews.enums import (
    ReviewSourceType,
    ReviewStatus,
    ReviewSubjectType,
)
from app.modules.reviews.exceptions import (
    ReviewConflictError,
    ReviewEligibilityError,
    ReviewLifecycleError,
    ReviewNotFoundError,
)
from app.modules.reviews.models import MarketplaceReview
from app.modules.reviews.repository import ReviewsRepository
from app.modules.reviews.schemas import ReviewCreateIn, ReviewOwnerOut, ReviewUpdateIn
from app.modules.services.enums import ServiceRequestStatus


class ReviewsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ReviewsRepository(db)

    def create(self, *, user: AuthUser, payload: ReviewCreateIn) -> ReviewOwnerOut:
        subject_owner_user_id = self._validate_eligibility(
            reviewer_user_id=user.id,
            source_type=payload.source_type,
            source_id=payload.source_id,
            subject_type=payload.subject_type,
            subject_id=payload.subject_id,
        )
        if subject_owner_user_id == user.id:
            raise ReviewEligibilityError("You cannot review your own business activity")

        existing = self.repo.get_existing(
            reviewer_user_id=user.id,
            source_type=payload.source_type.value,
            source_id=payload.source_id,
            subject_type=payload.subject_type.value,
            subject_id=payload.subject_id,
        )
        if existing is not None:
            raise ReviewConflictError(review_id=existing.id)

        row = MarketplaceReview(
            reviewer_user_id=user.id,
            source_type=payload.source_type.value,
            source_id=payload.source_id,
            subject_type=payload.subject_type.value,
            subject_id=payload.subject_id,
            score=payload.score,
            body=payload.body,
            status=ReviewStatus.ACTIVE.value,
        )
        try:
            self.repo.add(row)
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            existing = self.repo.get_existing(
                reviewer_user_id=user.id,
                source_type=payload.source_type.value,
                source_id=payload.source_id,
                subject_type=payload.subject_type.value,
                subject_id=payload.subject_id,
            )
            raise ReviewConflictError(
                review_id=None if existing is None else existing.id
            ) from exc
        return self._owner_out(row)

    def list_own(
        self,
        *,
        user: AuthUser,
        status: ReviewStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ReviewOwnerOut], int]:
        rows, total = self.repo.list_own(
            reviewer_user_id=user.id,
            status=None if status is None else status.value,
            page=page,
            page_size=page_size,
        )
        return [self._owner_out(row) for row in rows], total

    def get_own(self, *, user: AuthUser, review_id: int) -> ReviewOwnerOut:
        row = self.repo.get_own(
            review_id=review_id,
            reviewer_user_id=user.id,
        )
        if row is None:
            raise ReviewNotFoundError()
        return self._owner_out(row)

    def update(
        self,
        *,
        user: AuthUser,
        review_id: int,
        payload: ReviewUpdateIn,
    ) -> ReviewOwnerOut:
        if not payload.model_fields_set:
            raise ReviewEligibilityError("At least one review field is required")
        row = self.repo.get_own(
            review_id=review_id,
            reviewer_user_id=user.id,
            for_update=True,
        )
        if row is None:
            raise ReviewNotFoundError()
        if row.status != ReviewStatus.ACTIVE.value:
            raise ReviewLifecycleError(current_status=row.status)

        if "score" in payload.model_fields_set:
            if payload.score is None:
                raise ReviewEligibilityError("Review score cannot be null")
            row.score = payload.score
        if "body" in payload.model_fields_set:
            row.body = payload.body
        self.repo.commit()
        return self._owner_out(row)

    def delete(self, *, user: AuthUser, review_id: int) -> ReviewOwnerOut:
        row = self.repo.get_own(
            review_id=review_id,
            reviewer_user_id=user.id,
            for_update=True,
        )
        if row is None:
            raise ReviewNotFoundError()
        if row.status == ReviewStatus.DELETED.value:
            return self._owner_out(row)
        if row.status not in {
            ReviewStatus.ACTIVE.value,
            ReviewStatus.HIDDEN.value,
        }:
            raise ReviewLifecycleError(current_status=row.status)
        row.status = ReviewStatus.DELETED.value
        row.deleted_at = datetime.now(UTC).replace(tzinfo=None)
        self.repo.commit()
        return self._owner_out(row)

    def _validate_eligibility(
        self,
        *,
        reviewer_user_id: int,
        source_type: ReviewSourceType,
        source_id: int,
        subject_type: ReviewSubjectType,
        subject_id: int,
    ) -> int:
        if source_type == ReviewSourceType.ORDER:
            return self._validate_order(
                reviewer_user_id=reviewer_user_id,
                source_id=source_id,
                subject_type=subject_type,
                subject_id=subject_id,
            )
        if source_type == ReviewSourceType.SERVICE_REQUEST:
            return self._validate_service_request(
                reviewer_user_id=reviewer_user_id,
                source_id=source_id,
                subject_type=subject_type,
                subject_id=subject_id,
            )
        if source_type == ReviewSourceType.RENTAL_REQUEST:
            return self._validate_rental_request(
                reviewer_user_id=reviewer_user_id,
                source_id=source_id,
                subject_type=subject_type,
                subject_id=subject_id,
            )
        return self._validate_consult_request(
            reviewer_user_id=reviewer_user_id,
            source_id=source_id,
            subject_type=subject_type,
            subject_id=subject_id,
        )

    def _validate_order(
        self,
        *,
        reviewer_user_id: int,
        source_id: int,
        subject_type: ReviewSubjectType,
        subject_id: int,
    ) -> int:
        order = self.repo.get_order_for_update(source_id)
        self._require_owned_completed_source(
            row=order,
            owner_user_id=None if order is None else order.buyer_user_id,
            reviewer_user_id=reviewer_user_id,
            actual_status=None if order is None else order.status,
            required_status=OrderStatus.DELIVERED.value,
        )
        if subject_type == ReviewSubjectType.PRODUCT:
            if not self.repo.order_has_product(
                order_id=order.id,
                product_id=subject_id,
            ):
                raise ReviewEligibilityError("Product was not purchased in this order")
        elif subject_type == ReviewSubjectType.STORE:
            if subject_id != order.store_id:
                raise ReviewEligibilityError("Store does not belong to this order")
        else:
            self._raise_subject_mismatch(source_type=ReviewSourceType.ORDER)
        store = self.repo.get_store(order.store_id)
        if store is None:
            raise ReviewEligibilityError("Review subject is unavailable")
        return store.owner_user_id

    def _validate_service_request(
        self,
        *,
        reviewer_user_id: int,
        source_id: int,
        subject_type: ReviewSubjectType,
        subject_id: int,
    ) -> int:
        request = self.repo.get_service_request_for_update(source_id)
        self._require_owned_completed_source(
            row=request,
            owner_user_id=None if request is None else request.requester_user_id,
            reviewer_user_id=reviewer_user_id,
            actual_status=None if request is None else request.status,
            required_status=ServiceRequestStatus.COMPLETED.value,
        )
        if subject_type == ReviewSubjectType.SERVICE_OFFER:
            expected_id = request.offer_id
        elif subject_type == ReviewSubjectType.SERVICE_PROVIDER:
            expected_id = request.provider_profile_id
        else:
            self._raise_subject_mismatch(source_type=ReviewSourceType.SERVICE_REQUEST)
        if expected_id is None or subject_id != expected_id:
            raise ReviewEligibilityError("Review subject does not belong to this request")
        if request.provider_profile_id is None:
            raise ReviewEligibilityError("Service provider is unavailable")
        profile = self.repo.get_service_provider(request.provider_profile_id)
        if profile is None:
            raise ReviewEligibilityError("Review subject is unavailable")
        return profile.user_id

    def _validate_rental_request(
        self,
        *,
        reviewer_user_id: int,
        source_id: int,
        subject_type: ReviewSubjectType,
        subject_id: int,
    ) -> int:
        request = self.repo.get_rental_request_for_update(source_id)
        self._require_owned_completed_source(
            row=request,
            owner_user_id=None if request is None else request.requester_user_id,
            reviewer_user_id=reviewer_user_id,
            actual_status=None if request is None else request.status,
            required_status=RentalRequestStatus.COMPLETED.value,
        )
        if subject_type == ReviewSubjectType.RENTAL_EQUIPMENT:
            expected_id = request.equipment_id
        elif subject_type == ReviewSubjectType.RENTAL_LESSOR:
            expected_id = request.lessor_profile_id
        else:
            self._raise_subject_mismatch(source_type=ReviewSourceType.RENTAL_REQUEST)
        if subject_id != expected_id:
            raise ReviewEligibilityError("Review subject does not belong to this request")
        profile = self.repo.get_lessor_profile(request.lessor_profile_id)
        if profile is None:
            raise ReviewEligibilityError("Review subject is unavailable")
        return profile.user_id

    def _validate_consult_request(
        self,
        *,
        reviewer_user_id: int,
        source_id: int,
        subject_type: ReviewSubjectType,
        subject_id: int,
    ) -> int:
        request = self.repo.get_consult_request_for_update(source_id)
        self._require_owned_completed_source(
            row=request,
            owner_user_id=None if request is None else request.requester_user_id,
            reviewer_user_id=reviewer_user_id,
            actual_status=None if request is None else request.status,
            required_status=ConsultRequestStatus.COMPLETED.value,
        )
        if subject_type != ReviewSubjectType.CONSULTANT:
            self._raise_subject_mismatch(source_type=ReviewSourceType.CONSULT_REQUEST)
        if (
            request.consultant_profile_id is None
            or subject_id != request.consultant_profile_id
        ):
            raise ReviewEligibilityError("Consultant does not belong to this request")
        profile = self.repo.get_consultant_profile(request.consultant_profile_id)
        if profile is None:
            raise ReviewEligibilityError("Review subject is unavailable")
        return profile.user_id

    @staticmethod
    def _require_owned_completed_source(
        *,
        row: object | None,
        owner_user_id: int | None,
        reviewer_user_id: int,
        actual_status: str | None,
        required_status: str,
    ) -> None:
        if row is None:
            raise ReviewEligibilityError("Review source was not found")
        if owner_user_id != reviewer_user_id:
            raise PermissionDeniedError()
        if actual_status != required_status:
            raise ReviewEligibilityError(
                "Review source is not completed",
                details={
                    "current_status": actual_status,
                    "required_status": required_status,
                },
            )

    @staticmethod
    def _raise_subject_mismatch(*, source_type: ReviewSourceType) -> None:
        raise ReviewEligibilityError(
            "Review subject type is invalid for this source",
            details={"source_type": source_type.value},
        )

    @staticmethod
    def _owner_out(row: MarketplaceReview) -> ReviewOwnerOut:
        return ReviewOwnerOut(
            id=row.id,
            source_type=row.source_type,
            source_id=row.source_id,
            subject_type=row.subject_type,
            subject_id=row.subject_id,
            score=row.score,
            body=row.body,
            status=row.status,
            can_edit=row.status == ReviewStatus.ACTIVE.value,
            can_delete=row.status
            in {ReviewStatus.ACTIVE.value, ReviewStatus.HIDDEN.value},
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
        )
