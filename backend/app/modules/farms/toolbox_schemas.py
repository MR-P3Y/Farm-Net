from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.modules.farms.enums import (
    FarmCalculatorType,
    FarmFinancialCategory,
    FarmFinancialEntryType,
    FarmOperationType,
    FarmPlanStatus,
)


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip() or None


class FarmToolContextIn(BaseModel):
    plot_id: int | None = Field(default=None, ge=1)
    cycle_id: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def cycle_requires_plot(self):
        if self.cycle_id is not None and self.plot_id is None:
            raise ValueError("cycle_id requires plot_id")
        return self


class FarmToolCalculationCreateIn(FarmToolContextIn):
    calculator_type: FarmCalculatorType
    formula_version: Literal["1.0"] = "1.0"
    title: str = Field(min_length=1, max_length=180)
    input_values: dict[str, Decimal] = Field(min_length=1, max_length=20)
    input_units: dict[str, str] = Field(default_factory=dict, max_length=20)
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title is required")
        return value

    _notes = field_validator("notes")(_optional_text)

    @field_validator("input_units")
    @classmethod
    def validate_units(cls, value: dict[str, str]) -> dict[str, str]:
        normalized: dict[str, str] = {}
        for key, unit in value.items():
            clean_key = key.strip()
            clean_unit = unit.strip()
            if not clean_key or len(clean_key) > 80 or not clean_unit or len(clean_unit) > 40:
                raise ValueError("input unit keys and values must be bounded")
            normalized[clean_key] = clean_unit
        return normalized


class FarmToolCalculationOut(BaseModel):
    id: int
    farm_id: int
    plot_id: int | None
    cycle_id: int | None
    calculator_type: FarmCalculatorType
    formula_version: str
    title: str
    input_values: dict[str, Decimal]
    input_units: dict[str, str]
    result_values: dict[str, Decimal]
    result_units: dict[str, str]
    notes: str | None
    created_at: datetime


class FarmFinancialEntryCreateIn(FarmToolContextIn):
    entry_type: FarmFinancialEntryType
    category: FarmFinancialCategory
    amount_toman: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    occurred_on: date
    description: str | None = Field(default=None, max_length=500)

    _description = field_validator("description")(_optional_text)


class FarmFinancialEntryVoidIn(BaseModel):
    reason: str = Field(min_length=1, max_length=500)

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("reason is required")
        return value


class FarmFinancialEntryOut(FarmFinancialEntryCreateIn):
    id: int
    farm_id: int
    voided_at: datetime | None
    void_reason: str | None
    created_at: datetime

    @property
    def is_voided(self) -> bool:
        return self.voided_at is not None


class FarmFinancialSummaryOut(BaseModel):
    farm_id: int
    plot_id: int | None
    cycle_id: int | None
    expense_toman: Decimal
    revenue_toman: Decimal
    net_toman: Decimal
    active_entry_count: int


class FarmPlanCreateIn(FarmToolContextIn):
    operation_type: FarmOperationType
    title: str = Field(min_length=1, max_length=180)
    planned_for: date
    reminder_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title is required")
        return value

    _notes = field_validator("notes")(_optional_text)


class FarmPlanCompleteIn(BaseModel):
    occurred_on: date | None = None
    write_to_diary: bool = False


class FarmPlanCancelIn(BaseModel):
    reason: str | None = Field(default=None, max_length=500)

    _reason = field_validator("reason")(_optional_text)


class FarmPlanOut(FarmPlanCreateIn):
    id: int
    farm_id: int
    reminder_sent_at: datetime | None
    status: FarmPlanStatus
    completed_at: datetime | None
    cancelled_at: datetime | None
    cancel_reason: str | None
    farm_operation_id: int | None
    created_at: datetime
    updated_at: datetime


class FarmToolCalculationDetailResponse(BaseModel):
    success: bool
    data: FarmToolCalculationOut
    message: str
    meta: dict


class FarmToolCalculationListResponse(BaseModel):
    success: bool
    data: list[FarmToolCalculationOut]
    message: str
    meta: dict


class FarmFinancialEntryDetailResponse(BaseModel):
    success: bool
    data: FarmFinancialEntryOut
    message: str
    meta: dict


class FarmFinancialEntryListResponse(BaseModel):
    success: bool
    data: list[FarmFinancialEntryOut]
    message: str
    meta: dict


class FarmFinancialSummaryResponse(BaseModel):
    success: bool
    data: FarmFinancialSummaryOut
    message: str
    meta: dict


class FarmPlanDetailResponse(BaseModel):
    success: bool
    data: FarmPlanOut
    message: str
    meta: dict


class FarmPlanListResponse(BaseModel):
    success: bool
    data: list[FarmPlanOut]
    message: str
    meta: dict
