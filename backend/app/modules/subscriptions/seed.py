from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.subscriptions.models import BillingFeature, BillingPlan, BillingPlanFeature


@dataclass(frozen=True)
class FeatureSeed:
    code: str
    name: str
    module: str
    value_kind: str
    unit: str | None = None
    is_metered: bool = False
    is_safety_exempt: bool = False


FEATURES = (
    FeatureSeed("farms.max_count", "Maximum farms", "farms", "integer", "farm"),
    FeatureSeed("history.retention_days", "History retention", "history", "integer", "day"),
    FeatureSeed("reports.export_pdf", "PDF report export", "reports", "boolean"),
    FeatureSeed(
        "reports.deep_monthly", "Monthly deep reports", "reports", "integer", "report", True
    ),
    FeatureSeed("support.level", "Support level", "support", "string"),
    FeatureSeed("ai.text_chat", "AI text requests", "ai", "integer", "request", True),
    FeatureSeed("ai.farm_context", "AI farm-context requests", "ai", "integer", "request", True),
    FeatureSeed("ai.deep_analysis", "AI deep analyses", "ai", "integer", "analysis", True),
    FeatureSeed("ai.image_analysis", "AI image analyses", "ai", "integer", "image", True),
    FeatureSeed("ai.smart_diary", "AI smart diary", "ai", "boolean"),
    FeatureSeed("ai.report_export", "AI report export", "ai", "boolean"),
    FeatureSeed("ai.processing_priority", "AI processing priority", "ai", "string"),
    FeatureSeed(
        "store.products_max_count", "Maximum store products", "store", "integer", "product"
    ),
    FeatureSeed(
        "services.offers_max_count", "Maximum service offers", "services", "integer", "offer"
    ),
    FeatureSeed(
        "rentals.equipment_max_count",
        "Maximum rental equipment",
        "rentals",
        "integer",
        "equipment",
    ),
)

FREE_VALUES: dict[str, bool | int | str] = {
    "farms.max_count": 1,
    "history.retention_days": 30,
    "reports.export_pdf": False,
    "reports.deep_monthly": 0,
    "support.level": "community",
    "ai.text_chat": 20,
    "ai.farm_context": 8,
    "ai.deep_analysis": 0,
    "ai.image_analysis": 1,
    "ai.smart_diary": False,
    "ai.report_export": False,
    "ai.processing_priority": "standard",
    "store.products_max_count": 20,
    "services.offers_max_count": 3,
    "rentals.equipment_max_count": 3,
}


def seed_subscription_catalog(db: Session) -> dict[str, int]:
    features: dict[str, BillingFeature] = {}
    for item in FEATURES:
        row = db.query(BillingFeature).filter(BillingFeature.code == item.code).one_or_none()
        if row is None:
            row = BillingFeature(code=item.code)
            db.add(row)
        row.name = item.name
        row.module = item.module
        row.value_kind = item.value_kind
        row.unit = item.unit
        row.is_metered = item.is_metered
        row.is_safety_exempt = item.is_safety_exempt
        row.status = "active"
        features[item.code] = row

    db.flush()
    plan = (
        db.query(BillingPlan)
        .filter(BillingPlan.code == "free", BillingPlan.version == 1)
        .one_or_none()
    )
    if plan is None:
        plan = BillingPlan(code="free", version=1)
        db.add(plan)
    plan.name = "رایگان"
    plan.description = "دسترسی پایه و ایمن فارم نت"
    plan.status = "active"
    plan.billing_period = "free"
    plan.duration_days = None
    plan.price_toman = Decimal("0")
    plan.currency = "TOMAN"
    plan.is_default_free = True
    db.flush()

    for code, value in FREE_VALUES.items():
        feature = features[code]
        row = (
            db.query(BillingPlanFeature)
            .filter(
                BillingPlanFeature.plan_id == plan.id,
                BillingPlanFeature.feature_id == feature.id,
            )
            .one_or_none()
        )
        if row is None:
            row = BillingPlanFeature(plan_id=plan.id, feature_id=feature.id)
            db.add(row)
        row.is_enabled = bool(value) if feature.value_kind == "boolean" else True
        row.is_unlimited = False
        row.boolean_value = value if isinstance(value, bool) else None
        row.numeric_value = (
            Decimal(value)
            if feature.value_kind in {"integer", "decimal"} and not isinstance(value, bool)
            else None
        )
        row.string_value = value if isinstance(value, str) else None
        row.json_value = None

    db.commit()
    return {
        "features": len(FEATURES),
        "plans": db.query(BillingPlan).count(),
        "plan_features": db.query(BillingPlanFeature).filter_by(plan_id=plan.id).count(),
    }
