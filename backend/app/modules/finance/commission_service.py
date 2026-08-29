from decimal import Decimal

from sqlalchemy.orm import Session

from app.common.money import BillableSourceType
from app.modules.finance.enums import CommissionPolicyStatus
from app.modules.finance.models import CommissionPolicy
from app.modules.finance.schemas import CommissionPolicyOut
from app.modules.finance.seed import SERVICE_POLICY_CODE, SERVICE_POLICY_TITLE


class CommissionPolicyContractError(ValueError):
    pass


class CommissionPolicyService:
    EDITABLE_SOURCES = {BillableSourceType.SERVICE_REQUEST.value}

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_defaults(self) -> list[CommissionPolicyOut]:
        rows = (
            self.db.query(CommissionPolicy)
            .filter(CommissionPolicy.default_scope.is_not(None))
            .order_by(CommissionPolicy.source_type)
            .all()
        )
        return [self.output(row) for row in rows]

    def get_default(self, source_type: str) -> CommissionPolicyOut:
        return self.output(self._get(source_type))

    def update_default(
        self, *, source_type: str, percent: Decimal
    ) -> CommissionPolicyOut:
        if source_type not in self.EDITABLE_SOURCES:
            raise CommissionPolicyContractError("Commission source is not editable")
        row = (
            self.db.query(CommissionPolicy)
            .filter(CommissionPolicy.default_scope == source_type)
            .with_for_update()
            .one_or_none()
        )
        if row is None:
            row = CommissionPolicy(
                code=SERVICE_POLICY_CODE,
                title=SERVICE_POLICY_TITLE,
                source_type=source_type,
                default_scope=source_type,
                percent=percent,
                status=CommissionPolicyStatus.ACTIVE.value,
                is_default=True,
            )
            self.db.add(row)
        else:
            row.percent = percent
            row.status = CommissionPolicyStatus.ACTIVE.value
            row.is_default = True
        self.db.commit()
        self.db.refresh(row)
        return self.output(row)

    def _get(self, source_type: str) -> CommissionPolicy:
        if source_type not in self.EDITABLE_SOURCES:
            raise CommissionPolicyContractError("Commission source is not editable")
        row = (
            self.db.query(CommissionPolicy)
            .filter(
                CommissionPolicy.default_scope == source_type,
                CommissionPolicy.is_default.is_(True),
            )
            .one_or_none()
        )
        if row is None:
            raise CommissionPolicyContractError("Default commission policy not found")
        return row

    @staticmethod
    def output(row: CommissionPolicy) -> CommissionPolicyOut:
        return CommissionPolicyOut.model_validate(row, from_attributes=True)
