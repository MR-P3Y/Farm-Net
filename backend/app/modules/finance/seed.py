from decimal import Decimal

from sqlalchemy.orm import Session

from app.common.money import BillableSourceType
from app.modules.finance.enums import CommissionPolicyStatus
from app.modules.finance.models import CommissionPolicy


SERVICE_POLICY_CODE = "service-request-default"
SERVICE_POLICY_TITLE = "Default service request commission"
DEFAULT_SERVICE_COMMISSION_PERCENT = Decimal("10.00")


def seed_finance_policies(db: Session) -> dict[str, int | str]:
    row = (
        db.query(CommissionPolicy)
        .filter(CommissionPolicy.code == SERVICE_POLICY_CODE)
        .one_or_none()
    )
    created = 0
    updated = 0
    if row is None:
        row = CommissionPolicy(
            code=SERVICE_POLICY_CODE,
            title=SERVICE_POLICY_TITLE,
            source_type=BillableSourceType.SERVICE_REQUEST.value,
            default_scope=BillableSourceType.SERVICE_REQUEST.value,
            percent=DEFAULT_SERVICE_COMMISSION_PERCENT,
            status=CommissionPolicyStatus.ACTIVE.value,
            is_default=True,
        )
        db.add(row)
        db.flush()
        created = 1
    else:
        changed = False
        for name, value in (
            ("title", SERVICE_POLICY_TITLE),
            ("source_type", BillableSourceType.SERVICE_REQUEST.value),
            ("default_scope", BillableSourceType.SERVICE_REQUEST.value),
            ("status", CommissionPolicyStatus.ACTIVE.value),
            ("is_default", True),
        ):
            if getattr(row, name) != value:
                setattr(row, name, value)
                changed = True
        # The approved 10% is only the creation default. Never overwrite an
        # administrator-managed percentage on subsequent idempotent seed runs.
        if changed:
            updated = 1
        db.flush()

    db.commit()
    db.refresh(row)
    return {
        "created": created,
        "updated": updated,
        "service_policy_id": row.id,
        "service_percent": str(row.percent),
    }
