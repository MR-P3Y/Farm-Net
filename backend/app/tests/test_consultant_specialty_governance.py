from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

from app.modules.consultants.service import ConsultantService


def test_consultant_specialty_output_exposes_usage_counts():
    now = datetime.now()
    row = SimpleNamespace(
        id=1,
        code="plant_nutrition",
        title="تغذیه گیاه",
        description=None,
        sort_order=100,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    service = ConsultantService.__new__(ConsultantService)
    service.repo = Mock()
    service.repo.specialty_usage_counts.return_value = (7, 11)
    output = service._specialty_out(row)
    assert output.profiles_count == 7
    assert output.requests_count == 11
