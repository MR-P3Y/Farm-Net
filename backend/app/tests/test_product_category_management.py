import pytest
from pydantic import ValidationError

from app.modules.products.schemas import ProductCategoryCreateIn, ProductCategoryOut


def test_product_category_slug_contract_is_stable():
    payload = ProductCategoryCreateIn(name="بذر", slug="wheat-seeds", sort_order=10)
    assert payload.slug == "wheat-seeds"
    with pytest.raises(ValidationError):
        ProductCategoryCreateIn(name="بذر", slug="Wheat Seeds")


def test_product_category_admin_output_has_usage_counts():
    output = ProductCategoryOut(
        id=1,
        name="بذر",
        slug="seeds",
        sort_order=10,
        is_active=True,
        children_count=4,
        products_count=12,
        created_at="2026-07-18T00:00:00",
        updated_at="2026-07-18T00:00:00",
    )
    assert output.children_count == 4
    assert output.products_count == 12
