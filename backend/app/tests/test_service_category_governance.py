from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.services.schemas import ServiceCategoryUpdateIn
from app.modules.services.service import ServicesService


def service_with_categories(rows):
    service = ServicesService.__new__(ServicesService)
    service.repo = Mock()
    service.repo.get_category_by_id.side_effect = lambda category_id: rows.get(category_id)
    return service


def test_service_category_rejects_indirect_hierarchy_cycle():
    rows = {
        1: SimpleNamespace(id=1, parent_id=None),
        2: SimpleNamespace(id=2, parent_id=1),
        3: SimpleNamespace(id=3, parent_id=2),
    }
    service = service_with_categories(rows)
    with pytest.raises(ValidationAuthError):
        service._validate_parent_category(3, category_id=1)


def test_service_category_update_can_explicitly_clear_parent():
    payload = ServiceCategoryUpdateIn(parent_id=None)
    assert "parent_id" in payload.model_fields_set
    assert payload.parent_id is None


def test_service_category_output_includes_domain_usage_counts():
    now = datetime.now()
    row = SimpleNamespace(
        id=4,
        parent_id=None,
        code="harvesting",
        title="Harvesting",
        description=None,
        sort_order=10,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    service = service_with_categories({4: row})
    service.repo.category_usage_counts.return_value = (2, 3, 4, 5)
    output = service._category_out(row)
    assert (output.children_count, output.provider_links_count) == (2, 3)
    assert (output.offers_count, output.requests_count) == (4, 5)


def test_service_category_seed_does_not_overwrite_admin_owned_row():
    now = datetime.now()
    row = SimpleNamespace(
        id=1,
        parent_id=None,
        code="spraying",
        title="Admin title",
        description="Admin description",
        sort_order=999,
        is_active=False,
        created_at=now,
        updated_at=now,
    )
    service = service_with_categories({1: row})
    service.repo.get_category_by_code.return_value = row
    service.repo.category_usage_counts.return_value = (0, 0, 0, 0)
    service.seed_default_categories()
    assert row.title == "Admin title"
    assert row.sort_order == 999
    assert row.is_active is False
