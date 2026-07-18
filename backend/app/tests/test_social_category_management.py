from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.modules.social.schemas import SocialCategoryCreateIn
from app.modules.social.service import SocialService


def social_service() -> SocialService:
    service = SocialService.__new__(SocialService)
    service.repo = Mock()
    return service


def test_social_category_code_contract():
    assert SocialCategoryCreateIn(code="plant_health", title="سلامت گیاه").code == "plant_health"
    with pytest.raises(ValidationError):
        SocialCategoryCreateIn(code="Plant Health", title="سلامت گیاه")


def test_social_category_output_exposes_post_usage():
    now = datetime.now()
    row = SimpleNamespace(id=1, code="general", title="عمومی", description=None, sort_order=100, is_active=True, created_at=now, updated_at=now)
    service = social_service()
    service.repo.category_posts_count.return_value = 12
    assert service._category_out(row).posts_count == 12


def test_social_seed_preserves_admin_changes():
    now = datetime.now()
    row = SimpleNamespace(id=1, code="general", title="عنوان مدیر", description=None, sort_order=999, is_active=False, created_at=now, updated_at=now)
    service = social_service()
    service.repo.get_category_by_code.return_value = row
    service.repo.category_posts_count.return_value = 0
    service.seed_default_categories()
    assert row.title == "عنوان مدیر"
    assert row.sort_order == 999
    assert row.is_active is False
