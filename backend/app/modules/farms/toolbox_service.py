from datetime import UTC, date, datetime, time
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.auth.models import AuthUser
from app.modules.farms.enums import (
    CropCycleStatus,
    FarmCalculatorType,
    FarmFinancialEntryType,
    FarmPlanStatus,
)
from app.modules.farms.models import (
    Farm,
    FarmFinancialEntry,
    FarmOperation,
    FarmPlanItem,
    FarmToolCalculation,
)
from app.modules.farms.repository import FarmRepository
from app.modules.farms.service import FarmService
from app.modules.farms.toolbox_schemas import (
    FarmFinancialEntryCreateIn,
    FarmFinancialEntryOut,
    FarmFinancialSummaryOut,
    FarmPlanCancelIn,
    FarmPlanCompleteIn,
    FarmPlanCreateIn,
    FarmPlanOut,
    FarmToolCalculationCreateIn,
    FarmToolCalculationOut,
)
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.service import NotificationService


class FarmToolboxService:
    _formula_version = "1.0"
    _input_keys = {
        FarmCalculatorType.SEED: {
            "area_sqm",
            "row_spacing_m",
            "plant_spacing_m",
            "germination_percent",
            "reserve_percent",
        },
        FarmCalculatorType.IRRIGATION: {
            "area_sqm",
            "depth_mm",
            "efficiency_percent",
            "flow_lpm",
        },
        FarmCalculatorType.FERTILIZER: {
            "area_sqm",
            "rate_kg_per_hectare",
            "bag_size_kg",
        },
        FarmCalculatorType.SPRAYING: {
            "area_sqm",
            "water_rate_l_per_hectare",
            "product_rate_ml_per_l",
            "tank_capacity_l",
        },
        FarmCalculatorType.COST_PROFIT: {
            "total_cost_toman",
            "expected_yield_kg",
            "price_per_kg_toman",
            "area_sqm",
        },
        FarmCalculatorType.UNIT_CONVERSION: {"value", "factor"},
        FarmCalculatorType.PUMP_FUEL: {
            "flow_lpm",
            "target_volume_l",
            "fuel_l_per_hour",
            "fuel_price_toman",
        },
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FarmRepository(db)

    def create_calculation(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        payload: FarmToolCalculationCreateIn,
    ) -> FarmToolCalculationOut:
        farm = self._farm(user.id, farm_id, for_update=True)
        FarmService._require_active(farm)
        self._context(user.id, farm_id, payload.plot_id, payload.cycle_id)
        result_values, result_units = self.calculate(
            payload.calculator_type, payload.input_values
        )
        if payload.calculator_type == FarmCalculatorType.UNIT_CONVERSION:
            result_units["converted_value"] = payload.input_units.get(
                "to_unit", result_units["converted_value"]
            )
        row = self.repo.add(
            FarmToolCalculation(
                farm_id=farm.id,
                plot_id=payload.plot_id,
                cycle_id=payload.cycle_id,
                calculator_type=payload.calculator_type.value,
                formula_version=self._formula_version,
                title=payload.title,
                inputs_json={
                    "values": self._decimal_json(payload.input_values),
                    "units": payload.input_units,
                },
                results_json={
                    "values": self._decimal_json(result_values),
                    "units": result_units,
                },
                notes=payload.notes,
            )
        )
        self._audit(user.id, farm.id, "tool_calculation.created", "tool_calculation", row.id)
        self.db.commit()
        self.db.refresh(row)
        return self._calculation_out(row)

    def list_calculations(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        plot_id: int | None,
        cycle_id: int | None,
        calculator_type: FarmCalculatorType | None,
        limit: int,
    ) -> list[FarmToolCalculationOut]:
        self._farm(user.id, farm_id)
        self._context(user.id, farm_id, plot_id, cycle_id)
        query = self.db.query(FarmToolCalculation).filter(
            FarmToolCalculation.farm_id == farm_id
        )
        if plot_id is not None:
            query = query.filter(FarmToolCalculation.plot_id == plot_id)
        if cycle_id is not None:
            query = query.filter(FarmToolCalculation.cycle_id == cycle_id)
        if calculator_type is not None:
            query = query.filter(
                FarmToolCalculation.calculator_type == calculator_type.value
            )
        rows = query.order_by(
            FarmToolCalculation.created_at.desc(), FarmToolCalculation.id.desc()
        ).limit(min(max(limit, 1), 100)).all()
        return [self._calculation_out(row) for row in rows]

    @classmethod
    def calculate(
        cls,
        calculator_type: FarmCalculatorType,
        values: dict[str, Decimal],
    ) -> tuple[dict[str, Decimal], dict[str, str]]:
        expected = cls._input_keys[calculator_type]
        if set(values) != expected:
            raise AppException(
                "FARM_TOOL_INPUTS_INVALID",
                "Calculator inputs do not match the versioned formula",
                422,
                {"required_keys": sorted(expected)},
            )
        for key, value in values.items():
            if not value.is_finite() or value < 0:
                raise AppException(
                    "FARM_TOOL_VALUE_INVALID", f"Invalid calculator value: {key}", 422
                )
            if value > Decimal("1000000000000000"):
                raise AppException(
                    "FARM_TOOL_VALUE_TOO_LARGE", f"Calculator value is too large: {key}", 422
                )

        if calculator_type == FarmCalculatorType.SEED:
            cls._positive(values, "area_sqm", "row_spacing_m", "plant_spacing_m")
            cls._percent(values, "germination_percent", allow_zero=False)
            cls._percent(values, "reserve_percent", allow_zero=True)
            plants = values["area_sqm"] / (
                values["row_spacing_m"] * values["plant_spacing_m"]
            )
            seeds = plants / (values["germination_percent"] / Decimal(100))
            seeds *= Decimal(1) + values["reserve_percent"] / Decimal(100)
            return (
                {
                    "plant_count": plants.to_integral_value(rounding=ROUND_CEILING),
                    "seed_count": seeds.to_integral_value(rounding=ROUND_CEILING),
                },
                {"plant_count": "count", "seed_count": "count"},
            )

        if calculator_type == FarmCalculatorType.IRRIGATION:
            cls._positive(values, "area_sqm", "depth_mm", "flow_lpm")
            cls._percent(values, "efficiency_percent", allow_zero=False)
            volume = values["area_sqm"] * values["depth_mm"] / (
                values["efficiency_percent"] / Decimal(100)
            )
            return (
                {
                    "volume_l": cls._round(volume),
                    "duration_minutes": cls._round(volume / values["flow_lpm"]),
                },
                {"volume_l": "L", "duration_minutes": "min"},
            )

        if calculator_type == FarmCalculatorType.FERTILIZER:
            cls._positive(values, "area_sqm", "rate_kg_per_hectare", "bag_size_kg")
            total = values["area_sqm"] / Decimal(10000) * values["rate_kg_per_hectare"]
            return (
                {
                    "total_kg": cls._round(total),
                    "bag_count": (total / values["bag_size_kg"]).to_integral_value(
                        rounding=ROUND_CEILING
                    ),
                },
                {"total_kg": "kg", "bag_count": "bag"},
            )

        if calculator_type == FarmCalculatorType.SPRAYING:
            cls._positive(
                values,
                "area_sqm",
                "water_rate_l_per_hectare",
                "product_rate_ml_per_l",
                "tank_capacity_l",
            )
            water = values["area_sqm"] / Decimal(10000) * values[
                "water_rate_l_per_hectare"
            ]
            return (
                {
                    "water_l": cls._round(water),
                    "product_ml": cls._round(water * values["product_rate_ml_per_l"]),
                    "tank_count": (water / values["tank_capacity_l"]).to_integral_value(
                        rounding=ROUND_CEILING
                    ),
                },
                {"water_l": "L", "product_ml": "mL", "tank_count": "tank"},
            )

        if calculator_type == FarmCalculatorType.COST_PROFIT:
            cls._positive(values, "expected_yield_kg", "area_sqm")
            revenue = values["expected_yield_kg"] * values["price_per_kg_toman"]
            cost = values["total_cost_toman"]
            return (
                {
                    "expected_revenue_toman": cls._round(revenue, 2),
                    "profit_toman": cls._round(revenue - cost, 2),
                    "break_even_price_per_kg_toman": cls._round(
                        cost / values["expected_yield_kg"], 2
                    ),
                    "cost_per_sqm_toman": cls._round(cost / values["area_sqm"], 2),
                },
                {
                    "expected_revenue_toman": "TOMAN",
                    "profit_toman": "TOMAN",
                    "break_even_price_per_kg_toman": "TOMAN/kg",
                    "cost_per_sqm_toman": "TOMAN/m²",
                },
            )

        if calculator_type == FarmCalculatorType.UNIT_CONVERSION:
            cls._positive(values, "factor")
            return (
                {"converted_value": cls._round(values["value"] * values["factor"])},
                {"converted_value": "selected_unit"},
            )

        cls._positive(values, "flow_lpm", "target_volume_l")
        duration_minutes = values["target_volume_l"] / values["flow_lpm"]
        fuel_l = duration_minutes / Decimal(60) * values["fuel_l_per_hour"]
        return (
            {
                "duration_minutes": cls._round(duration_minutes),
                "fuel_l": cls._round(fuel_l),
                "fuel_cost_toman": cls._round(fuel_l * values["fuel_price_toman"], 2),
            },
            {
                "duration_minutes": "min",
                "fuel_l": "L",
                "fuel_cost_toman": "TOMAN",
            },
        )

    def create_financial_entry(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        payload: FarmFinancialEntryCreateIn,
    ) -> FarmFinancialEntryOut:
        farm = self._farm(user.id, farm_id, for_update=True)
        FarmService._require_active(farm)
        self._context(user.id, farm_id, payload.plot_id, payload.cycle_id)
        if payload.occurred_on > date.today():
            raise AppException(
                "FARM_FINANCIAL_DATE_INVALID", "Financial date cannot be in the future", 422
            )
        if (
            payload.entry_type == FarmFinancialEntryType.REVENUE
            and payload.category.value not in {"harvest_sale", "other"}
        ):
            raise AppException(
                "FARM_FINANCIAL_CATEGORY_INVALID",
                "Revenue category must be harvest_sale or other",
                422,
            )
        if (
            payload.entry_type == FarmFinancialEntryType.EXPENSE
            and payload.category.value == "harvest_sale"
        ):
            raise AppException(
                "FARM_FINANCIAL_CATEGORY_INVALID",
                "harvest_sale is a revenue category",
                422,
            )
        row = self.repo.add(
            FarmFinancialEntry(
                farm_id=farm.id,
                plot_id=payload.plot_id,
                cycle_id=payload.cycle_id,
                entry_type=payload.entry_type.value,
                category=payload.category.value,
                amount_toman=payload.amount_toman,
                occurred_on=payload.occurred_on,
                description=payload.description,
            )
        )
        self._audit(user.id, farm.id, "financial_entry.created", "financial_entry", row.id)
        self.db.commit()
        self.db.refresh(row)
        return self._financial_out(row)

    def list_financial_entries(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        plot_id: int | None,
        cycle_id: int | None,
        include_voided: bool,
        limit: int,
    ) -> list[FarmFinancialEntryOut]:
        self._farm(user.id, farm_id)
        self._context(user.id, farm_id, plot_id, cycle_id)
        query = self.db.query(FarmFinancialEntry).filter(
            FarmFinancialEntry.farm_id == farm_id
        )
        if plot_id is not None:
            query = query.filter(FarmFinancialEntry.plot_id == plot_id)
        if cycle_id is not None:
            query = query.filter(FarmFinancialEntry.cycle_id == cycle_id)
        if not include_voided:
            query = query.filter(FarmFinancialEntry.voided_at.is_(None))
        rows = query.order_by(
            FarmFinancialEntry.occurred_on.desc(), FarmFinancialEntry.id.desc()
        ).limit(min(max(limit, 1), 200)).all()
        return [self._financial_out(row) for row in rows]

    def financial_summary(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        plot_id: int | None,
        cycle_id: int | None,
    ) -> FarmFinancialSummaryOut:
        self._farm(user.id, farm_id)
        self._context(user.id, farm_id, plot_id, cycle_id)
        query = self.db.query(
            func.coalesce(
                func.sum(
                    case(
                        (
                            FarmFinancialEntry.entry_type
                            == FarmFinancialEntryType.EXPENSE.value,
                            FarmFinancialEntry.amount_toman,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            FarmFinancialEntry.entry_type
                            == FarmFinancialEntryType.REVENUE.value,
                            FarmFinancialEntry.amount_toman,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.count(FarmFinancialEntry.id),
        ).filter(
            FarmFinancialEntry.farm_id == farm_id,
            FarmFinancialEntry.voided_at.is_(None),
        )
        if plot_id is not None:
            query = query.filter(FarmFinancialEntry.plot_id == plot_id)
        if cycle_id is not None:
            query = query.filter(FarmFinancialEntry.cycle_id == cycle_id)
        expense, revenue, count = query.one()
        expense = Decimal(expense or 0)
        revenue = Decimal(revenue or 0)
        return FarmFinancialSummaryOut(
            farm_id=farm_id,
            plot_id=plot_id,
            cycle_id=cycle_id,
            expense_toman=expense,
            revenue_toman=revenue,
            net_toman=revenue - expense,
            active_entry_count=int(count or 0),
        )

    def void_financial_entry(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        entry_id: int,
        reason: str,
    ) -> FarmFinancialEntryOut:
        farm = self._farm(user.id, farm_id, for_update=True)
        FarmService._require_active(farm)
        row = self.db.query(FarmFinancialEntry).filter(
            FarmFinancialEntry.id == entry_id,
            FarmFinancialEntry.farm_id == farm.id,
        ).with_for_update().one_or_none()
        if row is None:
            raise AppException("FARM_FINANCIAL_ENTRY_NOT_FOUND", "Financial entry not found", 404)
        if row.voided_at is not None:
            raise AppException("FARM_FINANCIAL_ENTRY_VOIDED", "Financial entry is already voided", 409)
        row.voided_at = self._now()
        row.void_reason = reason
        self._audit(user.id, farm.id, "financial_entry.voided", "financial_entry", row.id)
        self.db.commit()
        self.db.refresh(row)
        return self._financial_out(row)

    def create_plan(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        payload: FarmPlanCreateIn,
    ) -> FarmPlanOut:
        farm = self._farm(user.id, farm_id, for_update=True)
        FarmService._require_active(farm)
        self._context(user.id, farm_id, payload.plot_id, payload.cycle_id)
        reminder_at = self._naive_utc(payload.reminder_at)
        if reminder_at is not None and reminder_at > datetime.combine(
            payload.planned_for, time.max
        ):
            raise AppException(
                "FARM_PLAN_REMINDER_INVALID",
                "Reminder cannot be later than the planned date",
                422,
            )
        row = self.repo.add(
            FarmPlanItem(
                farm_id=farm.id,
                plot_id=payload.plot_id,
                cycle_id=payload.cycle_id,
                operation_type=payload.operation_type.value,
                title=payload.title,
                planned_for=payload.planned_for,
                reminder_at=reminder_at,
                status=FarmPlanStatus.PLANNED.value,
                notes=payload.notes,
            )
        )
        self._audit(user.id, farm.id, "plan.created", "plan", row.id)
        self.db.commit()
        self.db.refresh(row)
        return self._plan_out(row)

    def list_plans(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        plot_id: int | None,
        cycle_id: int | None,
        status: FarmPlanStatus | None,
        limit: int,
    ) -> list[FarmPlanOut]:
        self._farm(user.id, farm_id)
        self._context(user.id, farm_id, plot_id, cycle_id)
        query = self.db.query(FarmPlanItem).filter(FarmPlanItem.farm_id == farm_id)
        if plot_id is not None:
            query = query.filter(FarmPlanItem.plot_id == plot_id)
        if cycle_id is not None:
            query = query.filter(FarmPlanItem.cycle_id == cycle_id)
        if status is not None:
            query = query.filter(FarmPlanItem.status == status.value)
        rows = query.order_by(FarmPlanItem.planned_for, FarmPlanItem.id).limit(
            min(max(limit, 1), 200)
        ).all()
        return [self._plan_out(row) for row in rows]

    def complete_plan(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        plan_id: int,
        payload: FarmPlanCompleteIn,
    ) -> FarmPlanOut:
        farm = self._farm(user.id, farm_id, for_update=True)
        FarmService._require_active(farm)
        row = self._plan(farm.id, plan_id, for_update=True)
        self._require_planned(row)
        operation = None
        if payload.write_to_diary:
            if row.plot_id is None or row.cycle_id is None:
                raise AppException(
                    "FARM_PLAN_DIARY_CONTEXT_REQUIRED",
                    "Plot and crop cycle are required for diary writing",
                    422,
                )
            cycle = self.repo.get_owned_cycle(
                farm_id=farm.id,
                plot_id=row.plot_id,
                cycle_id=row.cycle_id,
                owner_user_id=user.id,
                for_update=True,
            )
            if cycle is None:
                raise AppException("FARM_CROP_CYCLE_NOT_FOUND", "Crop cycle not found", 404)
            if cycle.status != CropCycleStatus.ACTIVE.value:
                raise AppException(
                    "FARM_CROP_CYCLE_NOT_ACTIVE",
                    "Diary records can only be added to an active crop cycle",
                    409,
                )
            occurred_on = payload.occurred_on or date.today()
            if occurred_on < cycle.actual_start_date:
                raise AppException(
                    "FARM_OPERATION_DATE_INVALID",
                    "Operation date cannot precede cycle start date",
                    422,
                )
            operation = self.repo.add(
                FarmOperation(
                    cycle_id=cycle.id,
                    operation_type=row.operation_type,
                    title=row.title,
                    occurred_on=occurred_on,
                    notes=row.notes,
                )
            )
            row.farm_operation_id = operation.id
            self._audit(user.id, farm.id, "operation.created", "operation", operation.id)
        row.status = FarmPlanStatus.COMPLETED.value
        row.completed_at = self._now()
        self._audit(user.id, farm.id, "plan.completed", "plan", row.id)
        self.db.commit()
        self.db.refresh(row)
        return self._plan_out(row)

    def cancel_plan(
        self,
        *,
        user: AuthUser,
        farm_id: int,
        plan_id: int,
        payload: FarmPlanCancelIn,
    ) -> FarmPlanOut:
        farm = self._farm(user.id, farm_id, for_update=True)
        FarmService._require_active(farm)
        row = self._plan(farm.id, plan_id, for_update=True)
        self._require_planned(row)
        row.status = FarmPlanStatus.CANCELLED.value
        row.cancelled_at = self._now()
        row.cancel_reason = payload.reason
        self._audit(user.id, farm.id, "plan.cancelled", "plan", row.id)
        self.db.commit()
        self.db.refresh(row)
        return self._plan_out(row)

    def dispatch_due_reminders(self, *, limit: int = 100) -> int:
        now = self._now()
        rows = (
            self.db.query(FarmPlanItem, Farm)
            .join(Farm, Farm.id == FarmPlanItem.farm_id)
            .filter(
                FarmPlanItem.status == FarmPlanStatus.PLANNED.value,
                FarmPlanItem.reminder_at.is_not(None),
                FarmPlanItem.reminder_at <= now,
                FarmPlanItem.reminder_sent_at.is_(None),
            )
            .order_by(FarmPlanItem.reminder_at, FarmPlanItem.id)
            .with_for_update(skip_locked=True)
            .limit(min(max(limit, 1), 500))
            .all()
        )
        notifications = NotificationService(self.db)
        for row, farm in rows:
            notifications.create_event_and_notify_user(
                event_type=NotificationEventType.FARM_PLAN_REMINDER.value,
                recipient_user_id=farm.owner_user_id,
                title="یادآوری عملیات مزرعه",
                body=f"{row.title} برای {row.planned_for.isoformat()} برنامه‌ریزی شده است.",
                source_type="farm_plan",
                source_id=str(row.id),
                payload_json={
                    "farm_id": row.farm_id,
                    "plot_id": row.plot_id,
                    "cycle_id": row.cycle_id,
                    "plan_id": row.id,
                    "planned_for": row.planned_for.isoformat(),
                },
                action_url=f"/toolbox?farmId={row.farm_id}",
                event_key=f"farm.plan_reminder:{row.id}",
                commit=False,
            )
            row.reminder_sent_at = now
        self.db.commit()
        return len(rows)

    def _farm(self, user_id: int, farm_id: int, for_update: bool = False) -> Farm:
        row = self.repo.get_owned(
            farm_id=farm_id, owner_user_id=user_id, for_update=for_update
        )
        if row is None:
            raise AppException("FARM_NOT_FOUND", "Farm not found", 404)
        return row

    def _context(
        self,
        user_id: int,
        farm_id: int,
        plot_id: int | None,
        cycle_id: int | None,
    ) -> None:
        if cycle_id is not None and plot_id is None:
            raise AppException("FARM_TOOL_CONTEXT_INVALID", "cycle_id requires plot_id", 422)
        if plot_id is not None:
            plot = self.repo.get_owned_plot(
                farm_id=farm_id, plot_id=plot_id, owner_user_id=user_id
            )
            if plot is None:
                raise AppException("FARM_PLOT_NOT_FOUND", "Farm plot not found", 404)
        if cycle_id is not None:
            cycle = self.repo.get_owned_cycle(
                farm_id=farm_id,
                plot_id=plot_id,
                cycle_id=cycle_id,
                owner_user_id=user_id,
            )
            if cycle is None:
                raise AppException("FARM_CROP_CYCLE_NOT_FOUND", "Crop cycle not found", 404)

    def _plan(self, farm_id: int, plan_id: int, for_update: bool = False) -> FarmPlanItem:
        query = self.db.query(FarmPlanItem).filter(
            FarmPlanItem.id == plan_id, FarmPlanItem.farm_id == farm_id
        )
        if for_update:
            query = query.with_for_update()
        row = query.one_or_none()
        if row is None:
            raise AppException("FARM_PLAN_NOT_FOUND", "Farm plan not found", 404)
        return row

    @staticmethod
    def _require_planned(row: FarmPlanItem) -> None:
        if row.status != FarmPlanStatus.PLANNED.value:
            raise AppException("FARM_PLAN_NOT_PLANNED", "Farm plan is not planned", 409)

    def _audit(
        self,
        actor_user_id: int,
        farm_id: int,
        action: str,
        target_type: str,
        target_id: int,
    ) -> None:
        self.repo.add_audit(
            farm_id=farm_id,
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
        )

    @staticmethod
    def _positive(cls_values: dict[str, Decimal], *keys: str) -> None:
        for key in keys:
            if cls_values[key] <= 0:
                raise AppException(
                    "FARM_TOOL_VALUE_INVALID", f"Calculator value must be positive: {key}", 422
                )

    @staticmethod
    def _percent(values: dict[str, Decimal], key: str, *, allow_zero: bool) -> None:
        minimum = Decimal(0) if allow_zero else Decimal("0.000001")
        if values[key] < minimum or values[key] > 100:
            raise AppException(
                "FARM_TOOL_PERCENT_INVALID", f"Calculator percentage is invalid: {key}", 422
            )

    @staticmethod
    def _round(value: Decimal, places: int = 6) -> Decimal:
        quantum = Decimal(1).scaleb(-places)
        return value.quantize(quantum, rounding=ROUND_HALF_UP).normalize()

    @staticmethod
    def _decimal_json(values: dict[str, Decimal]) -> dict[str, str]:
        return {key: format(value, "f") for key, value in values.items()}

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _naive_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.astimezone(UTC).replace(tzinfo=None)

    @staticmethod
    def _calculation_out(row: FarmToolCalculation) -> FarmToolCalculationOut:
        return FarmToolCalculationOut(
            id=row.id,
            farm_id=row.farm_id,
            plot_id=row.plot_id,
            cycle_id=row.cycle_id,
            calculator_type=row.calculator_type,
            formula_version=row.formula_version,
            title=row.title,
            input_values={
                key: Decimal(str(value)) for key, value in row.inputs_json["values"].items()
            },
            input_units=dict(row.inputs_json.get("units") or {}),
            result_values={
                key: Decimal(str(value)) for key, value in row.results_json["values"].items()
            },
            result_units=dict(row.results_json.get("units") or {}),
            notes=row.notes,
            created_at=row.created_at,
        )

    @staticmethod
    def _financial_out(row: FarmFinancialEntry) -> FarmFinancialEntryOut:
        return FarmFinancialEntryOut(
            id=row.id,
            farm_id=row.farm_id,
            plot_id=row.plot_id,
            cycle_id=row.cycle_id,
            entry_type=row.entry_type,
            category=row.category,
            amount_toman=row.amount_toman,
            occurred_on=row.occurred_on,
            description=row.description,
            voided_at=row.voided_at,
            void_reason=row.void_reason,
            created_at=row.created_at,
        )

    @staticmethod
    def _plan_out(row: FarmPlanItem) -> FarmPlanOut:
        return FarmPlanOut(
            id=row.id,
            farm_id=row.farm_id,
            plot_id=row.plot_id,
            cycle_id=row.cycle_id,
            operation_type=row.operation_type,
            title=row.title,
            planned_for=row.planned_for,
            reminder_at=row.reminder_at,
            reminder_sent_at=row.reminder_sent_at,
            status=row.status,
            notes=row.notes,
            completed_at=row.completed_at,
            cancelled_at=row.cancelled_at,
            cancel_reason=row.cancel_reason,
            farm_operation_id=row.farm_operation_id,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
