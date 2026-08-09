from sqlalchemy import CheckConstraint, UniqueConstraint

from app.main import app
from app.modules.auth.seed import BASE_PERMISSIONS
from app.modules.favorites.enums import FavoriteSubjectType
from app.modules.favorites.models import UserFavorite


def _constraint_names(constraint_type: type) -> set[str]:
    return {
        item.name
        for item in UserFavorite.__table__.constraints
        if isinstance(item, constraint_type) and item.name is not None
    }


def test_favorites_cover_every_public_discovery_domain() -> None:
    assert {item.value for item in FavoriteSubjectType} == {
        "product",
        "store",
        "service_offer",
        "rental_equipment",
        "consultant",
        "social_post",
    }


def test_favorites_are_owner_private_and_exact_once() -> None:
    assert UserFavorite.__tablename__ == "user_favorites"
    assert "uq_user_favorites_owner_subject" in _constraint_names(UniqueConstraint)
    assert {
        "ck_user_favorites_subject_id_positive",
        "ck_user_favorites_subject_type",
    } <= _constraint_names(CheckConstraint)


def test_favorite_permissions_and_openapi_are_complete() -> None:
    permissions = {item.code for item in BASE_PERMISSIONS}
    assert {"favorites.read_own", "favorites.manage_own"} <= permissions

    paths = app.openapi()["paths"]
    assert "/api/v1/favorites" in paths
    assert "/api/v1/favorites/status/{subject_type}" in paths
    assert "/api/v1/favorites/{subject_type}/{subject_id}" in paths
    assert {"put", "delete"} <= set(paths["/api/v1/favorites/{subject_type}/{subject_id}"])
