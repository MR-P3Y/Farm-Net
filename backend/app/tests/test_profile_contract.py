from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import AppException
from app.main import app
from app.modules.auth.exceptions import ValidationAuthError
from app.modules.profiles.schemas import ProfileUpdateIn
from app.modules.profiles.service import ProfileService


class _ProfileRepository:
    def __init__(self) -> None:
        self.profile = SimpleNamespace(
            id=1,
            user_id=7,
            first_name="Ali",
            last_name="Farmer",
            display_name="Old name",
            national_id="1234567890",
            birth_date=date(1990, 1, 1),
            gender="male",
            province_id=1,
            county_id=2,
            district_id=3,
            rural_district_id=4,
            city_id=5,
            village_id=6,
            address="Old address",
            postal_code="1234567890",
            avatar_file_id="owned-avatar-key",
            bio="Old bio",
        )

    def get_profile_by_user_id(self, user_id: int):
        assert user_id == 7
        return self.profile

    def create_profile(self, *, user_id: int):
        raise AssertionError(f"Unexpected profile creation for {user_id}")

    def get_profile_by_national_id(self, national_id: str):
        if national_id == "9876543210":
            return SimpleNamespace(user_id=99)
        if national_id == self.profile.national_id:
            return self.profile
        return None

    def get_province(self, province_id: int):
        return SimpleNamespace(id=province_id)

    def get_county(self, county_id: int):
        return SimpleNamespace(id=county_id, province_id=1)

    def get_district(self, district_id: int):
        return SimpleNamespace(id=district_id, province_id=1, county_id=2)

    def get_rural_district(self, rural_district_id: int):
        return SimpleNamespace(
            id=rural_district_id,
            province_id=1,
            county_id=2,
            district_id=3,
        )

    def get_city(self, city_id: int):
        return SimpleNamespace(id=city_id, province_id=1, county_id=2)

    def get_village(self, village_id: int):
        return SimpleNamespace(
            id=village_id,
            province_id=1,
            county_id=2,
            rural_district_id=4,
        )

    def commit(self) -> None:
        return None

    def get_active_profile_image_media(self, *, file_key: str, owner_user_id: int):
        if file_key == "owned-avatar-key" and owner_user_id == 7:
            return SimpleNamespace(file_key=file_key)
        return None

    def refresh(self, _instance) -> None:
        return None


def _service() -> tuple[ProfileService, _ProfileRepository]:
    service = ProfileService(MagicMock())
    repository = _ProfileRepository()
    service.repo = repository
    return service, repository


def test_profile_route_exposes_get_put_and_safe_patch() -> None:
    paths = app.openapi()["paths"]
    assert set(paths["/api/v1/profile/me"]) >= {"get", "put", "patch"}
    assert "/api/v1/profiles/me" not in paths


def test_partial_profile_update_preserves_fields_that_were_not_sent() -> None:
    service, repository = _service()

    result = service.update_my_profile(
        user=SimpleNamespace(id=7),
        payload=ProfileUpdateIn(display_name="New name"),
        partial=True,
    )

    assert result.display_name == "New name"
    assert repository.profile.avatar_file_id == "owned-avatar-key"
    assert repository.profile.district_id == 3
    assert repository.profile.rural_district_id == 4
    assert repository.profile.village_id == 6
    assert repository.profile.birth_date == date(1990, 1, 1)


def test_partial_profile_update_can_explicitly_clear_a_visible_field() -> None:
    service, repository = _service()

    service.update_my_profile(
        user=SimpleNamespace(id=7),
        payload=ProfileUpdateIn(display_name=None),
        partial=True,
    )

    assert repository.profile.display_name is None
    assert repository.profile.avatar_file_id == "owned-avatar-key"


def test_profile_rejects_a_future_birth_date() -> None:
    service, _repository = _service()

    with pytest.raises(ValidationAuthError):
        service.update_my_profile(
            user=SimpleNamespace(id=7),
            payload=ProfileUpdateIn(birth_date=date.today() + timedelta(days=1)),
            partial=True,
        )


def test_profile_rejects_a_national_id_owned_by_another_account() -> None:
    service, _repository = _service()

    with pytest.raises(AppException) as error:
        service.update_my_profile(
            user=SimpleNamespace(id=7),
            payload=ProfileUpdateIn(national_id="9876543210"),
            partial=True,
        )

    assert error.value.code == "PROFILE_NATIONAL_ID_CONFLICT"
    assert error.value.status_code == 409
    assert error.value.details == {"field": "national_id"}


def test_profile_completion_matches_verification_identity_requirements() -> None:
    service, repository = _service()
    assert service._is_profile_completed(repository.profile) is True

    repository.profile.national_id = None
    assert service._is_profile_completed(repository.profile) is False


def test_profile_avatar_must_be_owned_active_public_profile_media() -> None:
    service, _repository = _service()

    with pytest.raises(ValidationAuthError):
        service.update_my_profile(
            user=SimpleNamespace(id=7),
            payload=ProfileUpdateIn(avatar_file_id="another-users-file"),
            partial=True,
        )


def test_profile_avatar_returns_a_public_url_for_valid_owned_media() -> None:
    service, _repository = _service()

    result = service.update_my_profile(
        user=SimpleNamespace(id=7),
        payload=ProfileUpdateIn(avatar_file_id="owned-avatar-key"),
        partial=True,
    )

    assert result.avatar_url == "/api/v1/media/public/owned-avatar-key"
