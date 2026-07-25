from datetime import UTC, datetime, timedelta
from decimal import Decimal
from math import ceil

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import AppException
from app.modules.auth.models import AuthUser
from app.modules.subscriptions.admin_schemas import (
    AdminManualActivateIn,
    AdminPlanCreateIn,
    AdminPlanFeatureIn,
    AdminPlanOut,
    AdminPlanUpdateIn,
    AdminSubscriptionCancelIn,
    AdminSubscriptionDetailOut,
    AdminSubscriptionSummaryOut,
)
from app.modules.subscriptions.lifecycle_service import SubscriptionLifecycleService
from app.modules.subscriptions.models import (
    BillingFeature,
    BillingFeatureUsage,
    BillingPlan,
    BillingPlanFeature,
    BillingSubscription,
    BillingSubscriptionPeriod,
)
from app.modules.subscriptions.service import SubscriptionReadService


class AdminSubscriptionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_plans(
        self, *, q: str | None, status: str | None, page: int, page_size: int
    ) -> tuple[list[AdminPlanOut], int]:
        query = self.db.query(BillingPlan).options(
            joinedload(BillingPlan.features).joinedload(BillingPlanFeature.feature)
        )
        if q:
            term = f"%{q.strip()}%"
            query = query.filter(or_(BillingPlan.code.ilike(term), BillingPlan.name.ilike(term)))
        if status:
            query = query.filter(BillingPlan.status == status)
        total = query.count()
        rows = (
            query.order_by(BillingPlan.code, BillingPlan.version.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return [self._plan_out(row) for row in rows], total

    def create_plan(self, payload: AdminPlanCreateIn) -> AdminPlanOut:
        self._validate_period(payload.billing_period, payload.duration_days, payload.price_toman)
        latest_version = (
            self.db.query(BillingPlan.version)
            .filter(BillingPlan.code == payload.code)
            .order_by(BillingPlan.version.desc())
            .limit(1)
            .scalar()
            or 0
        )
        row = BillingPlan(
            code=payload.code,
            version=latest_version + 1,
            name=payload.name.strip(),
            description=self._clean(payload.description),
            status="draft",
            billing_period=payload.billing_period,
            duration_days=payload.duration_days,
            price_toman=payload.price_toman,
            currency="TOMAN",
            is_default_free=False,
            effective_from=payload.effective_from,
            effective_until=payload.effective_until,
        )
        self._validate_range(row.effective_from, row.effective_until)
        self.db.add(row)
        self.db.flush()
        self._replace_features(row, payload.features)
        self.db.commit()
        return self._plan_out(row)

    def update_plan(self, plan_id: int, payload: AdminPlanUpdateIn) -> AdminPlanOut:
        row = self._plan(plan_id, lock=True)
        if row.status != "draft":
            raise AppException(
                "BILLING_PLAN_IMMUTABLE",
                "Only draft plans can be edited",
                409,
            )
        if row.version != payload.expected_version:
            raise AppException("BILLING_PLAN_VERSION_CONFLICT", "Plan version conflict", 409)
        values = payload.model_fields_set
        for field in (
            "name",
            "description",
            "billing_period",
            "duration_days",
            "price_toman",
            "effective_from",
            "effective_until",
        ):
            if field in values:
                value = getattr(payload, field)
                if field == "name" and value is not None:
                    value = value.strip()
                if field == "description":
                    value = self._clean(value)
                setattr(row, field, value)
        self._validate_period(row.billing_period, row.duration_days, row.price_toman)
        self._validate_range(row.effective_from, row.effective_until)
        if payload.features is not None:
            self._replace_features(row, payload.features)
        self.db.commit()
        return self._plan_out(row)

    def set_plan_status(self, plan_id: int, *, expected_version: int, status: str) -> AdminPlanOut:
        row = self._plan(plan_id, lock=True)
        if row.version != expected_version:
            raise AppException("BILLING_PLAN_VERSION_CONFLICT", "Plan version conflict", 409)
        if status == "active":
            if row.status != "draft":
                raise AppException(
                    "BILLING_PLAN_INVALID_TRANSITION",
                    "Only draft plans can be activated",
                    409,
                )
            if not row.features:
                raise AppException(
                    "BILLING_PLAN_FEATURES_REQUIRED",
                    "An active plan requires features",
                    422,
                )
            (
                self.db.query(BillingPlan)
                .filter(
                    BillingPlan.code == row.code,
                    BillingPlan.status == "active",
                    BillingPlan.id != row.id,
                )
                .update({"status": "retired"}, synchronize_session=False)
            )
            row.status = "active"
        elif status == "retired":
            if row.is_default_free:
                raise AppException(
                    "BILLING_DEFAULT_FREE_REQUIRED",
                    "The default Free plan cannot be retired",
                    409,
                )
            if row.status == "retired":
                return self._plan_out(row)
            row.status = "retired"
        self.db.commit()
        return self._plan_out(row)

    def list_subscriptions(
        self,
        *,
        q: str | None,
        status: str | None,
        plan_id: int | None,
        user_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[AdminSubscriptionSummaryOut], int]:
        query = (
            self.db.query(BillingSubscription)
            .join(BillingSubscription.plan)
            .join(AuthUser, AuthUser.id == BillingSubscription.user_id)
            .options(joinedload(BillingSubscription.plan))
        )
        if q:
            term = f"%{q.strip()}%"
            query = query.filter(or_(AuthUser.email.ilike(term), AuthUser.phone.ilike(term)))
        if status:
            query = query.filter(BillingSubscription.status == status)
        if plan_id:
            query = query.filter(BillingSubscription.plan_id == plan_id)
        if user_id:
            query = query.filter(BillingSubscription.user_id == user_id)
        total = query.count()
        rows = (
            query.order_by(BillingSubscription.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        labels = self._user_labels({row.user_id for row in rows})
        return [self._subscription_summary(row, labels) for row in rows], total

    def subscription_detail(self, subscription_id: int) -> AdminSubscriptionDetailOut:
        row = self._subscription(subscription_id)
        usages = (
            self.db.query(BillingFeatureUsage)
            .options(joinedload(BillingFeatureUsage.entitlement))
            .filter(
                BillingFeatureUsage.user_id == row.user_id,
                BillingFeatureUsage.period_id.in_(
                    self.db.query(BillingSubscriptionPeriod.id).filter(
                        BillingSubscriptionPeriod.subscription_id == row.id
                    )
                ),
            )
            .order_by(BillingFeatureUsage.id)
            .all()
        )
        summary = self._subscription_summary(row, self._user_labels({row.user_id})).model_dump()
        return AdminSubscriptionDetailOut(
            **summary,
            current_period_starts_at=row.current_period_starts_at,
            cancelled_at=row.cancelled_at,
            ended_at=row.ended_at,
            cancellation_reason=row.cancellation_reason,
            usage=[SubscriptionReadService.usage_output(item) for item in usages],
        )

    def manual_activate(
        self, *, admin_user_id: int, payload: AdminManualActivateIn
    ) -> AdminSubscriptionDetailOut:
        now = _utcnow()
        user = (
            self.db.query(AuthUser)
            .filter(AuthUser.id == payload.user_id, AuthUser.deleted_at.is_(None))
            .with_for_update()
            .one_or_none()
        )
        if user is None:
            raise AppException("BILLING_USER_NOT_FOUND", "User not found", 404)
        current = (
            self.db.query(BillingSubscription.id)
            .filter(
                BillingSubscription.user_id == payload.user_id,
                BillingSubscription.status.in_(("active", "grace")),
            )
            .first()
        )
        if current:
            raise AppException(
                "BILLING_ACTIVE_SUBSCRIPTION_EXISTS",
                "User already has an active subscription",
                409,
            )
        plan = self._plan(payload.plan_id, lock=True)
        if plan.status != "active":
            raise AppException("BILLING_PLAN_NOT_ACTIVE", "Only active plans can be assigned", 409)
        ends_at = now + timedelta(days=self._duration_days(plan))
        subscription = BillingSubscription(
            user_id=user.id,
            plan_id=plan.id,
            plan=plan,
            status="active",
            starts_at=now,
            current_period_starts_at=now,
            current_period_ends_at=ends_at,
            auto_renew=False,
            cancel_at_period_end=False,
            activation_source="admin",
            activated_by_user_id=admin_user_id,
            activation_reason=payload.reason.strip(),
            version=1,
        )
        self.db.add(subscription)
        self.db.flush()
        period = BillingSubscriptionPeriod(
            subscription_id=subscription.id,
            sequence=1,
            status="active",
            starts_at=now,
            ends_at=ends_at,
            invoice_id=None,
            plan_code_snapshot=plan.code,
            plan_version_snapshot=plan.version,
            price_toman_snapshot=plan.price_toman,
            currency="TOMAN",
        )
        self.db.add(period)
        self.db.flush()
        SubscriptionLifecycleService(self.db)._snapshot_entitlements(
            user_id=user.id,
            subscription=subscription,
            period=period,
            values=plan.features,
            source="admin",
        )
        self.db.commit()
        return self.subscription_detail(subscription.id)

    def cancel_subscription(
        self, subscription_id: int, payload: AdminSubscriptionCancelIn
    ) -> AdminSubscriptionDetailOut:
        row = self._subscription(subscription_id, lock=True)
        if row.version != payload.expected_version:
            raise AppException(
                "BILLING_SUBSCRIPTION_VERSION_CONFLICT",
                "Subscription version conflict",
                409,
            )
        if row.status not in {"active", "grace"}:
            raise AppException(
                "BILLING_SUBSCRIPTION_NOT_CANCELLABLE",
                "Subscription cannot be cancelled in its current state",
                409,
            )
        now = _utcnow()
        row.cancellation_reason = payload.reason.strip()
        row.auto_renew = False
        if payload.cancel_at_period_end:
            row.cancel_at_period_end = True
        else:
            row.status = "cancelled"
            row.cancel_at_period_end = False
            row.cancelled_at = now
            row.ended_at = now
            period = (
                self.db.query(BillingSubscriptionPeriod)
                .filter(
                    BillingSubscriptionPeriod.subscription_id == row.id,
                    BillingSubscriptionPeriod.status == "active",
                )
                .with_for_update()
                .one_or_none()
            )
            if period:
                effective_end = max(now, period.starts_at + timedelta(seconds=1))
                period.ends_at = effective_end
                period.status = "closed"
                for entitlement in row.entitlements:
                    entitlement.ends_at = effective_end
        row.version += 1
        self.db.commit()
        return self.subscription_detail(row.id)

    def _plan(self, plan_id: int, *, lock: bool = False) -> BillingPlan:
        query = (
            self.db.query(BillingPlan)
            .options(joinedload(BillingPlan.features).joinedload(BillingPlanFeature.feature))
            .filter(BillingPlan.id == plan_id)
        )
        if lock:
            query = query.with_for_update()
        row = query.one_or_none()
        if row is None:
            raise AppException("BILLING_PLAN_NOT_FOUND", "Plan not found", 404)
        return row

    def _subscription(self, subscription_id: int, *, lock: bool = False) -> BillingSubscription:
        query = (
            self.db.query(BillingSubscription)
            .options(
                joinedload(BillingSubscription.plan),
                joinedload(BillingSubscription.entitlements),
            )
            .filter(BillingSubscription.id == subscription_id)
        )
        if lock:
            query = query.with_for_update()
        row = query.one_or_none()
        if row is None:
            raise AppException("BILLING_SUBSCRIPTION_NOT_FOUND", "Subscription not found", 404)
        return row

    def _replace_features(self, plan: BillingPlan, values: list[AdminPlanFeatureIn]) -> None:
        codes = [item.feature_code for item in values]
        if len(codes) != len(set(codes)):
            raise AppException("BILLING_DUPLICATE_FEATURE", "Feature codes must be unique", 422)
        features = {
            row.code: row
            for row in self.db.query(BillingFeature)
            .filter(BillingFeature.code.in_(codes), BillingFeature.status == "active")
            .all()
        }
        missing = sorted(set(codes) - set(features))
        if missing:
            raise AppException(
                "BILLING_FEATURE_NOT_FOUND",
                f"Unknown active features: {', '.join(missing)}",
                422,
            )
        plan.features.clear()
        self.db.flush()
        for item in values:
            feature = features[item.feature_code]
            self._validate_feature_value(feature, item)
            plan.features.append(
                BillingPlanFeature(
                    feature_id=feature.id,
                    feature=feature,
                    is_enabled=item.enabled,
                    is_unlimited=item.unlimited,
                    boolean_value=item.boolean_value,
                    numeric_value=item.numeric_value,
                    string_value=item.string_value,
                    json_value=item.json_value,
                )
            )
        self.db.flush()

    @staticmethod
    def _validate_feature_value(feature: BillingFeature, value: AdminPlanFeatureIn) -> None:
        supplied = {
            "boolean": value.boolean_value,
            "integer": value.numeric_value,
            "decimal": value.numeric_value,
            "string": value.string_value,
            "json": value.json_value,
        }[feature.value_kind]
        if value.enabled and not value.unlimited and supplied is None:
            raise AppException(
                "BILLING_FEATURE_VALUE_REQUIRED",
                f"A value is required for {feature.code}",
                422,
            )
        if value.unlimited and not feature.is_metered:
            raise AppException(
                "BILLING_FEATURE_UNLIMITED_INVALID",
                f"Unlimited is only valid for metered feature {feature.code}",
                422,
            )

    @staticmethod
    def _validate_period(
        billing_period: str, duration_days: int | None, price_toman: Decimal
    ) -> None:
        if billing_period == "free" and price_toman != 0:
            raise AppException("BILLING_FREE_PLAN_PRICE", "Free plans must have a zero price", 422)
        if (billing_period == "custom") != (duration_days is not None):
            raise AppException(
                "BILLING_CUSTOM_DURATION",
                "Custom plans require duration_days and other plans forbid it",
                422,
            )

    @staticmethod
    def _validate_range(start: datetime | None, end: datetime | None) -> None:
        if start and end and end <= start:
            raise AppException(
                "BILLING_EFFECTIVE_RANGE",
                "effective_until must be after effective_from",
                422,
            )

    @staticmethod
    def _duration_days(plan: BillingPlan) -> int:
        if plan.billing_period == "monthly":
            return 30
        if plan.billing_period == "yearly":
            return 365
        if plan.billing_period == "custom" and plan.duration_days:
            return plan.duration_days
        return 30

    @staticmethod
    def _clean(value: str | None) -> str | None:
        cleaned = value.strip() if value else ""
        return cleaned or None

    @staticmethod
    def _plan_out(row: BillingPlan) -> AdminPlanOut:
        base = SubscriptionReadService.plan_output(row).model_dump()
        return AdminPlanOut(
            **base,
            status=row.status,
            effective_from=row.effective_from,
            effective_until=row.effective_until,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _subscription_summary(
        row: BillingSubscription, labels: dict[int, str]
    ) -> AdminSubscriptionSummaryOut:
        return AdminSubscriptionSummaryOut(
            id=row.id,
            user_id=row.user_id,
            user_label=labels.get(row.user_id, f"User #{row.user_id}"),
            status=row.status,
            plan_id=row.plan_id,
            plan_code=row.plan.code,
            plan_name=row.plan.name,
            price_toman=row.plan.price_toman,
            currency=row.plan.currency,
            starts_at=row.starts_at,
            current_period_ends_at=row.current_period_ends_at,
            grace_ends_at=row.grace_ends_at,
            auto_renew=row.auto_renew,
            cancel_at_period_end=row.cancel_at_period_end,
            activation_source=row.activation_source,
            activated_by_user_id=row.activated_by_user_id,
            activation_reason=row.activation_reason,
            version=row.version,
            created_at=row.created_at,
        )

    def _user_labels(self, user_ids: set[int]) -> dict[int, str]:
        if not user_ids:
            return {}
        return {
            row.id: row.email or row.phone or f"User #{row.id}"
            for row in self.db.query(AuthUser).filter(AuthUser.id.in_(user_ids)).all()
        }


def page_meta(*, page: int, page_size: int, total: int, trace_id: str) -> dict[str, int | str]:
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": ceil(total / page_size) if total else 0,
        "trace_id": trace_id,
    }


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
