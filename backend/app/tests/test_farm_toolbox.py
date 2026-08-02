import json
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint

from app.core.exceptions import AppException
from app.main import app
from app.modules.farms.enums import (
    FarmCalculatorType,
    FarmFinancialCategory,
    FarmFinancialEntryType,
    FarmPlanStatus,
)
from app.modules.farms.models import (
    FarmFinancialEntry,
    FarmPlanItem,
    FarmToolCalculation,
)
from app.modules.farms.toolbox_schemas import FarmToolCalculationCreateIn
from app.modules.farms.toolbox_service import FarmToolboxService
from app.modules.notifications.enums import NotificationEventType


def _checks(model) -> set[str]:
    return {item.name for item in model.__table__.constraints if isinstance(item, CheckConstraint)}


def test_toolbox_database_and_enum_contracts_are_explicit() -> None:
    assert "ck_farm_tool_calculations_type" in _checks(FarmToolCalculation)
    assert "ck_farm_financial_amount_positive" in _checks(FarmFinancialEntry)
    assert "ck_farm_financial_void_state" in _checks(FarmFinancialEntry)
    assert "ck_farm_plan_items_lifecycle" in _checks(FarmPlanItem)
    assert "ck_farm_plan_items_reminder_state" in _checks(FarmPlanItem)
    assert {item.value for item in FarmCalculatorType} == {
        "seed",
        "irrigation",
        "fertilizer",
        "spraying",
        "cost_profit",
        "unit_conversion",
        "pump_fuel",
    }
    assert {item.value for item in FarmFinancialEntryType} == {"expense", "revenue"}
    assert "harvest_sale" in {item.value for item in FarmFinancialCategory}
    assert {item.value for item in FarmPlanStatus} == {
        "planned",
        "completed",
        "cancelled",
    }
    assert NotificationEventType.FARM_PLAN_REMINDER.value == "farm.plan_reminder"


@pytest.mark.parametrize(
    ("calculator_type", "inputs", "expected"),
    [
        (
            FarmCalculatorType.SEED,
            {
                "area_sqm": Decimal("10000"),
                "row_spacing_m": Decimal("1"),
                "plant_spacing_m": Decimal("0.5"),
                "germination_percent": Decimal("80"),
                "reserve_percent": Decimal("10"),
            },
            {"plant_count": Decimal("20000"), "seed_count": Decimal("27500")},
        ),
        (
            FarmCalculatorType.IRRIGATION,
            {
                "area_sqm": Decimal("1000"),
                "depth_mm": Decimal("10"),
                "efficiency_percent": Decimal("80"),
                "flow_lpm": Decimal("100"),
            },
            {"volume_l": Decimal("12500"), "duration_minutes": Decimal("125")},
        ),
        (
            FarmCalculatorType.FERTILIZER,
            {
                "area_sqm": Decimal("5000"),
                "rate_kg_per_hectare": Decimal("200"),
                "bag_size_kg": Decimal("25"),
            },
            {"total_kg": Decimal("100"), "bag_count": Decimal("4")},
        ),
        (
            FarmCalculatorType.SPRAYING,
            {
                "area_sqm": Decimal("10000"),
                "water_rate_l_per_hectare": Decimal("500"),
                "product_rate_ml_per_l": Decimal("2"),
                "tank_capacity_l": Decimal("200"),
            },
            {
                "water_l": Decimal("500"),
                "product_ml": Decimal("1000"),
                "tank_count": Decimal("3"),
            },
        ),
        (
            FarmCalculatorType.COST_PROFIT,
            {
                "total_cost_toman": Decimal("1000000"),
                "expected_yield_kg": Decimal("1000"),
                "price_per_kg_toman": Decimal("1500"),
                "area_sqm": Decimal("10000"),
            },
            {
                "expected_revenue_toman": Decimal("1500000"),
                "profit_toman": Decimal("500000"),
                "break_even_price_per_kg_toman": Decimal("1000"),
                "cost_per_sqm_toman": Decimal("100"),
            },
        ),
        (
            FarmCalculatorType.UNIT_CONVERSION,
            {"value": Decimal("10000"), "factor": Decimal("0.0001")},
            {"converted_value": Decimal("1")},
        ),
        (
            FarmCalculatorType.PUMP_FUEL,
            {
                "flow_lpm": Decimal("100"),
                "target_volume_l": Decimal("6000"),
                "fuel_l_per_hour": Decimal("2"),
                "fuel_price_toman": Decimal("10000"),
            },
            {
                "duration_minutes": Decimal("60"),
                "fuel_l": Decimal("2"),
                "fuel_cost_toman": Decimal("20000"),
            },
        ),
    ],
)
def test_versioned_calculators_recompute_authoritative_results(
    calculator_type: FarmCalculatorType,
    inputs: dict[str, Decimal],
    expected: dict[str, Decimal],
) -> None:
    result, units = FarmToolboxService.calculate(calculator_type, inputs)
    assert result == expected
    assert set(result) == set(units)


def test_calculator_rejects_missing_keys_and_unsafe_percentages() -> None:
    with pytest.raises(AppException) as missing:
        FarmToolboxService.calculate(FarmCalculatorType.UNIT_CONVERSION, {"value": Decimal("1")})
    assert missing.value.code == "FARM_TOOL_INPUTS_INVALID"

    with pytest.raises(AppException) as percent:
        FarmToolboxService.calculate(
            FarmCalculatorType.SEED,
            {
                "area_sqm": Decimal("100"),
                "row_spacing_m": Decimal("1"),
                "plant_spacing_m": Decimal("1"),
                "germination_percent": Decimal("101"),
                "reserve_percent": Decimal("0"),
            },
        )
    assert percent.value.code == "FARM_TOOL_PERCENT_INVALID"


def test_calculation_schema_requires_a_plot_for_cycle_context() -> None:
    with pytest.raises(ValidationError):
        FarmToolCalculationCreateIn(
            cycle_id=7,
            calculator_type="unit_conversion",
            title="Area conversion",
            input_values={"value": 10000, "factor": Decimal("0.0001")},
        )


def test_toolbox_routes_are_owner_private_and_complete() -> None:
    paths = app.openapi()["paths"]
    root = "/api/v1/farms/{farm_id}/toolbox"
    expected = {
        f"{root}/calculations",
        f"{root}/costs",
        f"{root}/costs/{{entry_id}}/void",
        f"{root}/cost-summary",
        f"{root}/plans",
        f"{root}/plans/{{plan_id}}/complete",
        f"{root}/plans/{{plan_id}}/cancel",
    }
    assert expected.issubset(paths)
    assert not any("/public/" in path and "/toolbox" in path for path in paths)


def test_notification_worker_dispatches_due_plan_reminders() -> None:
    source = (
        Path(__file__).resolve().parents[2] / "scripts" / "run_notification_worker.py"
    ).read_text(encoding="utf-8")
    assert "dispatch_due_reminders" in source
    assert "farm_plan_reminders" in source


def test_farm_toolbox_postman_and_docs_cover_the_route_contract() -> None:
    root = Path(__file__).resolve().parents[3]
    collection = json.loads(
        (root / "postman" / "collections" / "farms.postman_collection.json").read_text(
            encoding="utf-8"
        )
    )
    toolbox = next(item for item in collection["item"] if item["name"] == "Farm toolbox")
    urls = {item["request"]["url"] for item in toolbox["item"]}
    assert len(toolbox["item"]) == 10
    assert "{{base_url}}/farms/:farm_id/toolbox/calculations" in urls
    assert (
        "{{base_url}}/farms/:farm_id/toolbox/cost-summary?plot_id={{plot_id}}&cycle_id={{cycle_id}}"
        in urls
    )
    assert "{{base_url}}/farms/:farm_id/toolbox/plans/:plan_id/complete" in urls
    api_docs = (root / "docs" / "api" / "farms.md").read_text(encoding="utf-8")
    assert "Farm toolbox endpoints" in api_docs
    assert "formula `1.0`" in api_docs
