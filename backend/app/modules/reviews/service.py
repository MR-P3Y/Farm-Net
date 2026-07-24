from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import PermissionDeniedError
from app.modules.auth.models import AuthUser
from app.modules.consultants.enums import ConsultRequestStatus
from app.modules.orders.enums import OrderStatus
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.service import NotificationService
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
    ReviewReportConflictError,
    ReviewReportNotFoundError,
)
from app.modules.reviews.models import (
    MarketplaceReview,
    MarketplaceReviewModerationLog,
    MarketplaceReviewReport,
)
from app.modules.reviews.repository import ReviewsRepository
from app.modules.reviews.schemas import (
    RatingSummaryOut,
    ReviewCreateIn,
    ReviewAdminOut,
    ReviewModerationIn,
    ReviewModerationLogOut,
    ReviewOwnerOut,
    ReviewPublicAuthorOut,
    ReviewPublicOut,
    ReviewReportAdminOut,
    ReviewReportCreateIn,
    ReviewReportOwnerOut,
    ReviewReportResolutionIn,
    ReviewUpdateIn,
)
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
            self._apply_rating_delta(
                subject_type=payload.subject_type.value,
                subject_id=payload.subject_id,
                rating_delta=payload.score,
                count_delta=1,
            )
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

        previous_score = row.score
        if "score" in payload.model_fields_set:
            if payload.score is None:
                raise ReviewEligibilityError("Review score cannot be null")
            row.score = payload.score
        if "body" in payload.model_fields_set:
            row.body = payload.body
        if row.score != previous_score:
            self._apply_rating_delta(
                subject_type=row.subject_type,
                subject_id=row.subject_id,
                rating_delta=row.score - previous_score,
                count_delta=0,
            )
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
        was_active = row.status == ReviewStatus.ACTIVE.value
        row.status = ReviewStatus.DELETED.value
        row.deleted_at = datetime.now(UTC).replace(tzinfo=None)
        if was_active:
            self._apply_rating_delta(
                subject_type=row.subject_type,
                subject_id=row.subject_id,
                rating_delta=-row.score,
                count_delta=-1,
            )
        self.repo.commit()
        return self._owner_out(row)

    def list_public(
        self,
        *,
        subject_type: ReviewSubjectType,
        subject_id: int,
        page: int,
        page_size: int,
    ) -> tuple[list[ReviewPublicOut], int, RatingSummaryOut]:
        if not self.repo.public_subject_exists(
            subject_type=subject_type.value,
            subject_id=subject_id,
        ):
            raise ReviewNotFoundError()
        rows, total = self.repo.list_public(
            subject_type=subject_type.value,
            subject_id=subject_id,
            page=page,
            page_size=page_size,
        )
        aggregate = self.repo.get_aggregate(
            subject_type=subject_type.value,
            subject_id=subject_id,
        )
        summary = RatingSummaryOut(
            subject_type=subject_type.value,
            subject_id=subject_id,
            rating_average=(
                Decimal("0.00") if aggregate is None else aggregate.rating_average
            ),
            reviews_count=0 if aggregate is None else aggregate.reviews_count,
        )
        items = [
            ReviewPublicOut(
                id=review.id,
                score=review.score,
                body=review.body,
                author=ReviewPublicAuthorOut(
                    display_name=self._public_author_name(profile)
                ),
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
            for review, profile in rows
        ]
        return items, total, summary

    def report(
        self, *, user: AuthUser, review_id: int, payload: ReviewReportCreateIn
    ) -> ReviewReportOwnerOut:
        review = self.repo.get_review(review_id)
        if review is None or review.status != ReviewStatus.ACTIVE.value:
            raise ReviewNotFoundError()
        if review.reviewer_user_id == user.id:
            raise ReviewEligibilityError("You cannot report your own review")
        existing = self.repo.get_report_by_reporter(
            review_id=review_id, reporter_user_id=user.id
        )
        if existing is not None:
            raise ReviewReportConflictError(report_id=existing.id)
        row = MarketplaceReviewReport(
            review_id=review_id,
            reporter_user_id=user.id,
            reason=payload.reason.value,
            description=payload.description,
            status="open",
        )
        try:
            self.repo.add_report(row)
            self._notify_review_reported(
                report=row,
                actor_user_id=user.id,
            )
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            existing = self.repo.get_report_by_reporter(
                review_id=review_id, reporter_user_id=user.id
            )
            raise ReviewReportConflictError(
                report_id=None if existing is None else existing.id
            ) from exc
        return ReviewReportOwnerOut.model_validate(row, from_attributes=True)

    def list_admin_reviews(self, *, status, page: int, page_size: int):
        rows, total = self.repo.list_admin_reviews(
            status=None if status is None else status.value,
            page=page,
            page_size=page_size,
        )
        return [ReviewAdminOut.model_validate(row) for row in rows], total

    def moderate_review(
        self,
        *,
        admin_user_id: int,
        review_id: int,
        payload: ReviewModerationIn,
    ) -> ReviewAdminOut:
        row = self.repo.get_review(review_id, for_update=True)
        if row is None:
            raise ReviewNotFoundError()
        target = payload.status.value
        if target not in {
            ReviewStatus.ACTIVE.value,
            ReviewStatus.HIDDEN.value,
            ReviewStatus.DELETED.value,
        }:
            raise ReviewLifecycleError(current_status=row.status)
        if row.status == ReviewStatus.DELETED.value and target != row.status:
            raise ReviewLifecycleError(current_status=row.status)
        if target == row.status:
            return ReviewAdminOut.model_validate(row)
        old_status = row.status
        if old_status == ReviewStatus.ACTIVE.value:
            self._apply_rating_delta(
                subject_type=row.subject_type,
                subject_id=row.subject_id,
                rating_delta=-row.score,
                count_delta=-1,
            )
        elif target == ReviewStatus.ACTIVE.value:
            self._apply_rating_delta(
                subject_type=row.subject_type,
                subject_id=row.subject_id,
                rating_delta=row.score,
                count_delta=1,
            )
        row.status = target
        row.deleted_at = (
            datetime.now(UTC).replace(tzinfo=None)
            if target == ReviewStatus.DELETED.value
            else None
        )
        action = {
            ReviewStatus.ACTIVE.value: "restored",
            ReviewStatus.HIDDEN.value: "hidden",
            ReviewStatus.DELETED.value: "deleted",
        }[target]
        log = self.repo.add_moderation_log(
            MarketplaceReviewModerationLog(
                review_id=row.id,
                actor_user_id=admin_user_id,
                action=action,
                from_status=old_status,
                to_status=target,
                note=payload.note,
                event_key=f"review:{row.id}:{action}:{uuid4().hex}",
            )
        )
        self._notify_review_moderated(
            review=row,
            actor_user_id=admin_user_id,
            action=action,
            event_key=f"review-moderation:{log.id}",
        )
        self.repo.commit()
        return ReviewAdminOut.model_validate(row)

    def list_admin_reports(self, *, status, page: int, page_size: int):
        rows, total = self.repo.list_admin_reports(
            status=None if status is None else status.value,
            page=page,
            page_size=page_size,
        )
        return [ReviewReportAdminOut.model_validate(row) for row in rows], total

    def resolve_report(
        self,
        *,
        admin_user_id: int,
        report_id: int,
        payload: ReviewReportResolutionIn,
    ) -> ReviewReportAdminOut:
        report = self.repo.get_report(report_id, for_update=True)
        if report is None:
            raise ReviewReportNotFoundError()
        target = payload.status.value
        if target == "open":
            raise ReviewLifecycleError(current_status=report.status)
        if report.status in {"resolved", "dismissed"}:
            if report.status == target:
                return ReviewReportAdminOut.model_validate(report)
            raise ReviewLifecycleError(current_status=report.status)
        report.status = target
        report.reviewed_by_user_id = admin_user_id
        report.resolution_note = payload.resolution_note
        report.reviewed_at = datetime.now(UTC).replace(tzinfo=None)
        action = f"report_{target}"
        log = self.repo.add_moderation_log(
            MarketplaceReviewModerationLog(
                review_id=report.review_id,
                actor_user_id=admin_user_id,
                report_id=report.id,
                action=action,
                note=payload.resolution_note,
                event_key=f"report:{report.id}:{action}:{uuid4().hex}",
            )
        )
        self._notify_report_resolution(
            report=report,
            actor_user_id=admin_user_id,
            event_key=f"review-report-resolution:{log.id}",
        )
        self.repo.commit()
        return ReviewReportAdminOut.model_validate(report)

    def moderation_logs(self, *, review_id: int):
        if self.repo.get_review(review_id) is None:
            raise ReviewNotFoundError()
        return [
            ReviewModerationLogOut.model_validate(row)
            for row in self.repo.list_moderation_logs(review_id)
        ]

    def _apply_rating_delta(
        self,
        *,
        subject_type: str,
        subject_id: int,
        rating_delta: int,
        count_delta: int,
    ) -> None:
        aggregate = self.repo.get_or_create_aggregate(
            subject_type=subject_type,
            subject_id=subject_id,
        )
        rating_sum = aggregate.rating_sum + rating_delta
        reviews_count = aggregate.reviews_count + count_delta
        if reviews_count < 0 or rating_sum < 0:
            raise ReviewLifecycleError(current_status="aggregate_inconsistent")
        aggregate.rating_sum = rating_sum
        aggregate.reviews_count = reviews_count
        aggregate.rating_average = (
            Decimal("0.00")
            if reviews_count == 0
            else (Decimal(rating_sum) / Decimal(reviews_count)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        )
        self.repo.sync_legacy_rating_projection(
            subject_type=subject_type,
            subject_id=subject_id,
            rating_average=aggregate.rating_average,
            reviews_count=reviews_count,
        )

    def _notify_review_reported(
        self, *, report: MarketplaceReviewReport, actor_user_id: int
    ) -> None:
        recipient_ids = self.repo.list_recipient_user_ids_for_permission(
            "review_reports.admin_read"
        )
        if not recipient_ids:
            return
        NotificationService(self.db).create_event_and_notify_many(
            event_type=NotificationEventType.REVIEW_REPORTED.value,
            recipient_user_ids=recipient_ids,
            title="گزارش جدید برای یک نظر",
            body="یک نظر عمومی برای بررسی مدیریتی گزارش شد.",
            actor_user_id=actor_user_id,
            source_type="review_report",
            source_id=str(report.id),
            payload_json={
                "report_id": report.id,
                "review_id": report.review_id,
                "reason": report.reason,
            },
            action_url="/admin/reviews/reports",
            priority="high",
            event_key=f"review-report-created:{report.id}",
            commit=False,
        )

    def _notify_review_moderated(
        self,
        *,
        review: MarketplaceReview,
        actor_user_id: int,
        action: str,
        event_key: str,
    ) -> None:
        event_type = {
            "hidden": NotificationEventType.REVIEW_HIDDEN.value,
            "restored": NotificationEventType.REVIEW_RESTORED.value,
            "deleted": NotificationEventType.REVIEW_DELETED.value,
        }[action]
        title = {
            "hidden": "نظر شما مخفی شد",
            "restored": "نظر شما بازیابی شد",
            "deleted": "نظر شما حذف شد",
        }[action]
        NotificationService(self.db).create_event_and_notify_user(
            event_type=event_type,
            recipient_user_id=review.reviewer_user_id,
            title=title,
            body="وضعیت نظر شما پس از بررسی مدیریتی تغییر کرد.",
            actor_user_id=actor_user_id,
            source_type="review",
            source_id=str(review.id),
            payload_json={"review_id": review.id, "status": review.status},
            action_url="/reviews/me",
            event_key=event_key,
            commit=False,
        )

    def _notify_report_resolution(
        self,
        *,
        report: MarketplaceReviewReport,
        actor_user_id: int,
        event_key: str,
    ) -> None:
        event_type = {
            "reviewed": NotificationEventType.REVIEW_REPORT_REVIEWED.value,
            "resolved": NotificationEventType.REVIEW_REPORT_RESOLVED.value,
            "dismissed": NotificationEventType.REVIEW_REPORT_DISMISSED.value,
        }[report.status]
        NotificationService(self.db).create_event_and_notify_user(
            event_type=event_type,
            recipient_user_id=report.reporter_user_id,
            title="نتیجه بررسی گزارش نظر",
            body="وضعیت گزارش شما پس از بررسی مدیریتی به‌روزرسانی شد.",
            actor_user_id=actor_user_id,
            source_type="review_report",
            source_id=str(report.id),
            payload_json={
                "report_id": report.id,
                "review_id": report.review_id,
                "status": report.status,
            },
            action_url="/notifications",
            event_key=event_key,
            commit=False,
        )

    @staticmethod
    def _public_author_name(profile) -> str:
        if profile is None:
            return "کاربر فارم‌نت"
        display_name = getattr(profile, "display_name", None)
        if display_name and display_name.strip():
            return display_name.strip()
        full_name = " ".join(
            part.strip()
            for part in (
                getattr(profile, "first_name", None),
                getattr(profile, "last_name", None),
            )
            if part and part.strip()
        )
        return full_name or "کاربر فارم‌نت"

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
