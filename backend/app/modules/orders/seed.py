from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.geo import models as geo_models  # noqa: F401
from app.modules.orders.enums import CommissionSettingStatus
from app.modules.orders.models import CommissionSetting
from app.modules.products import models as product_models  # noqa: F401
from app.modules.stores import models as store_models  # noqa: F401


DEFAULT_COMMISSION_TITLE = "Default platform commission"
DEFAULT_COMMISSION_PERCENT = Decimal("5.00")


def seed_commission_settings(db: Session) -> dict[str, int | str]:
    created = 0
    updated = 0

    default_setting = (
        db.query(CommissionSetting)
        .filter(CommissionSetting.is_default.is_(True))
        .one_or_none()
    )

    if default_setting is None:
        default_setting = CommissionSetting(
            title=DEFAULT_COMMISSION_TITLE,
            percent=DEFAULT_COMMISSION_PERCENT,
            status=CommissionSettingStatus.ACTIVE.value,
            is_default=True,
            description="Default commission used for new orders. Admin can change it later.",
        )
        db.add(default_setting)
        db.flush()
        created += 1
    else:
        changed = False

        if default_setting.title != DEFAULT_COMMISSION_TITLE:
            default_setting.title = DEFAULT_COMMISSION_TITLE
            changed = True

        # IMPORTANT:
        # Do not overwrite default_setting.percent here.
        # Admin can update commission percent through Admin Commission APIs.
        # Seed must stay idempotent and must not reset admin-managed values.

        if default_setting.status != CommissionSettingStatus.ACTIVE.value:
            default_setting.status = CommissionSettingStatus.ACTIVE.value
            changed = True

        if default_setting.is_default is not True:
            default_setting.is_default = True
            changed = True

        if changed:
            updated += 1

        db.flush()

    (
        db.query(CommissionSetting)
        .filter(
            CommissionSetting.id != default_setting.id,
            CommissionSetting.is_default.is_(True),
        )
        .update(
            {
                CommissionSetting.is_default: False,
                CommissionSetting.status: CommissionSettingStatus.INACTIVE.value,
            },
            synchronize_session=False,
        )
    )

    db.commit()

    total = db.query(CommissionSetting).count()
    active = (
        db.query(CommissionSetting)
        .filter(CommissionSetting.status == CommissionSettingStatus.ACTIVE.value)
        .count()
    )

    return {
        "total": total,
        "active": active,
        "created": created,
        "updated": updated,
        "default_id": default_setting.id,
        "default_percent": str(default_setting.percent),
    }
