import pytest
from pydantic import ValidationError

from app.common.money import BillableSourceRef, BillableSourceType, CurrencyCode
from app.modules.consultants.schemas import ConsultRequestCreateIn
from app.modules.products.schemas import ProductCreateIn
from app.modules.rentals.schemas import RentalPricingRuleIn
from app.modules.services.schemas import ServiceRequestCreateIn


def test_billable_source_contract_is_toman_only() -> None:
    row = BillableSourceRef(
        source_type=BillableSourceType.RENTAL_REQUEST,
        source_id=7,
        payer_user_id=11,
        provider_user_id=13,
        currency="toman",
    )
    assert row.currency == CurrencyCode.TOMAN

    with pytest.raises(ValidationError):
        BillableSourceRef(
            source_type="rental_request",
            source_id=7,
            payer_user_id=11,
            provider_user_id=13,
            currency="IRR",
        )


@pytest.mark.parametrize(
    ("schema", "payload"),
    [
        (
            ConsultRequestCreateIn,
            {"title": "مشاوره کشت", "description": "شرح معتبر درخواست مشاوره"},
        ),
        (
            ServiceRequestCreateIn,
            {"offer_id": 1, "title": "خدمت", "description": "شرح معتبر خدمت"},
        ),
        (
            RentalPricingRuleIn,
            {"unit": "day", "price_amount": "1000"},
        ),
        (
            ProductCreateIn,
            {"name": "محصول", "slug": "product", "price": "1000"},
        ),
    ],
)
def test_new_commercial_inputs_default_to_toman(schema, payload) -> None:
    assert schema(**payload).currency == "TOMAN"
    with pytest.raises(ValidationError):
        schema(**payload, currency="IRR")
