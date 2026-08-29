from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.core.exceptions import AppException
from app.main import app
from app.modules.auth.schemas import AuthUserOut, EmailRegisterIn, TokenPairOut
from app.modules.auth.service import AuthService
from app.modules.profiles.schemas import ProfileUpdateIn
from app.modules.profiles.service import ProfileService


def _registration_payload(**overrides):
    data = {
        "email": "farmer@example.com",
        "password": "strong-password",
        "first_name": "Ali",
        "last_name": "Farmer",
        "national_id": "1234567890",
        "province_id": 1,
        "county_id": 2,
        "address": "Farm road",
    }
    data.update(overrides)
    return data


def test_registration_schema_requires_complete_profile_fields() -> None:
    with pytest.raises(ValidationError):
        EmailRegisterIn(email="farmer@example.com", password="strong-password")


def test_registration_schema_normalizes_profile_text_and_local_digits() -> None:
    payload = EmailRegisterIn(
        **_registration_payload(
            first_name="  علی  ",
            national_id="۱۲۳۴۵۶۷۸۹۰",
            postal_code="١٢٣٤٥٦٧٨٩٠",
        )
    )

    assert payload.first_name == "علی"
    assert payload.national_id == "1234567890"
    assert payload.postal_code == "1234567890"


def test_registration_openapi_marks_profile_completion_fields_required() -> None:
    schema = app.openapi()["components"]["schemas"]["EmailRegisterIn"]
    assert set(schema["required"]) >= {
        "email",
        "password",
        "first_name",
        "last_name",
        "national_id",
        "province_id",
        "county_id",
        "address",
    }


class _RegistrationProfileRepository:
    def __init__(self) -> None:
        self.profile = None
        self.commits = 0

    def get_profile_by_user_id(self, user_id: int):
        return self.profile

    def get_profile_by_national_id(self, national_id: str):
        return None

    def get_province(self, province_id: int):
        return SimpleNamespace(id=province_id)

    def get_county(self, county_id: int):
        return SimpleNamespace(id=county_id, province_id=1)

    def get_city(self, city_id: int):
        return SimpleNamespace(id=city_id, province_id=1, county_id=2)

    def create_profile(self, *, user_id: int):
        self.profile = SimpleNamespace(user_id=user_id)
        return self.profile

    def commit(self) -> None:
        self.commits += 1


def test_registration_profile_is_prepared_without_an_early_commit() -> None:
    service = ProfileService(MagicMock())
    repository = _RegistrationProfileRepository()
    service.repo = repository
    payload = ProfileUpdateIn(
        first_name="Ali",
        last_name="Farmer",
        national_id="1234567890",
        province_id=1,
        county_id=2,
        city_id=3,
        address="Farm road",
    )

    profile = service.prepare_registration_profile(
        user=SimpleNamespace(id=9),
        payload=payload,
    )

    assert profile.user_id == 9
    assert profile.national_id == "1234567890"
    assert profile.address == "Farm road"
    assert repository.commits == 0


class _AuthRegistrationRepository:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0
        self.user = SimpleNamespace(
            id=9,
            email="farmer@example.com",
            phone=None,
            status="active",
            is_email_verified=False,
            is_phone_verified=False,
        )

    def get_user_by_email(self, email: str):
        return None

    def create_user(self, **_kwargs):
        return self.user

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def test_registration_commits_account_and_profile_once(monkeypatch) -> None:
    repository = _AuthRegistrationRepository()
    service = AuthService.__new__(AuthService)
    service.db = MagicMock()
    service.repo = repository
    service.settings = SimpleNamespace()
    prepared = []
    expected_token = TokenPairOut(
        access_token="access",
        refresh_token="refresh",
        user=AuthUserOut(
            id=9,
            email="farmer@example.com",
            status="active",
            is_email_verified=False,
            is_phone_verified=False,
        ),
    )
    monkeypatch.setattr(
        "app.modules.auth.service.ProfileService.prepare_registration_profile",
        lambda _self, *, user, payload: prepared.append((user.id, payload)),
    )
    monkeypatch.setattr(service, "_assign_base_user_role", lambda _user: None)
    monkeypatch.setattr(
        service,
        "_create_token_pair",
        lambda **_kwargs: expected_token,
    )
    monkeypatch.setattr(
        "app.modules.auth.service.hash_password",
        lambda value: f"hashed:{value}",
    )
    profile = ProfileUpdateIn(
        first_name="Ali",
        last_name="Farmer",
        national_id="1234567890",
        province_id=1,
        county_id=2,
        address="Farm road",
    )

    result = service.register_with_email(
        email="farmer@example.com",
        password="strong-password",
        profile=profile,
    )

    assert result == expected_token
    assert prepared == [(9, profile)]
    assert repository.commits == 1
    assert repository.rollbacks == 0


def test_registration_rolls_back_when_profile_validation_fails(monkeypatch) -> None:
    repository = _AuthRegistrationRepository()
    service = AuthService.__new__(AuthService)
    service.db = MagicMock()
    service.repo = repository
    service.settings = SimpleNamespace()
    def reject_profile(*_args, **_kwargs):
        raise AppException(
            code="PROFILE_NATIONAL_ID_CONFLICT",
            message="Conflict",
            status_code=409,
        )

    monkeypatch.setattr(
        "app.modules.auth.service.ProfileService.prepare_registration_profile",
        reject_profile,
    )
    monkeypatch.setattr(
        "app.modules.auth.service.hash_password",
        lambda value: f"hashed:{value}",
    )

    with pytest.raises(AppException):
        service.register_with_email(
            email="farmer@example.com",
            password="strong-password",
            profile=ProfileUpdateIn(
                first_name="Ali",
                last_name="Farmer",
                national_id="1234567890",
                province_id=1,
                county_id=2,
                address="Farm road",
            ),
        )

    assert repository.commits == 0
    assert repository.rollbacks == 1
