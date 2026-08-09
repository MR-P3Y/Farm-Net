from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.modules.favorites.enums import FavoriteSubjectType
from app.modules.favorites.exceptions import FavoriteSubjectNotFoundError
from app.modules.favorites.models import UserFavorite
from app.modules.favorites.service import FavoritesService


def _favorite(subject_type: str, subject_id: int) -> UserFavorite:
    row = UserFavorite(user_id=7, subject_type=subject_type, subject_id=subject_id)
    row.id = 19
    row.created_at = datetime(2026, 8, 10, 10, 30)
    return row


def test_add_product_is_idempotent_and_returns_navigation_snapshot() -> None:
    repo = Mock()
    product = SimpleNamespace(
        id=11,
        name="بذر گندم",
        short_description="بذر گواهی‌شده",
        images=[],
        store=SimpleNamespace(name="فروشگاه سبز"),
    )
    row = _favorite("product", 11)
    repo.public_subject.return_value = product
    repo.get_existing.return_value = None
    repo.add_exact_once.return_value = (row, True)
    repo.public_media_url.return_value = None

    result, created = FavoritesService(None, repo).add(
        user_id=7,
        subject_type=FavoriteSubjectType.PRODUCT,
        subject_id=11,
    )

    assert created is True
    assert result.title == "بذر گندم"
    assert result.route == "/products/11"
    repo.commit.assert_called_once()


def test_add_rejects_missing_or_non_public_subject() -> None:
    repo = Mock()
    repo.public_subject.return_value = None

    with pytest.raises(FavoriteSubjectNotFoundError):
        FavoritesService(None, repo).add(
            user_id=7,
            subject_type=FavoriteSubjectType.SERVICE_OFFER,
            subject_id=99,
        )

    repo.add_exact_once.assert_not_called()
    repo.commit.assert_not_called()


def test_social_favorite_keeps_legacy_bookmark_compatible() -> None:
    repo = Mock()
    post = SimpleNamespace(
        id=5,
        title="تجربه کشت",
        body="متن تجربه",
        media_file_id=None,
    )
    row = _favorite("social_post", 5)
    repo.public_subject.return_value = post
    repo.get_existing.return_value = row
    repo.public_media_url.return_value = None

    result, created = FavoritesService(None, repo).add(
        user_id=7,
        subject_type=FavoriteSubjectType.SOCIAL_POST,
        subject_id=5,
    )

    assert created is False
    assert result.route == "/social/detail/5"
    repo.sync_legacy_social_add.assert_called_once_with(user_id=7, post_id=5)


def test_remove_is_idempotent_and_social_cleanup_is_symmetric() -> None:
    repo = Mock()
    repo.get_existing.return_value = None

    removed = FavoritesService(None, repo).remove(
        user_id=7,
        subject_type=FavoriteSubjectType.SOCIAL_POST,
        subject_id=5,
    )

    assert removed is False
    repo.delete.assert_not_called()
    repo.sync_legacy_social_delete.assert_called_once_with(user_id=7, post_id=5)
    repo.commit.assert_called_once()


def test_status_deduplicates_requested_ids() -> None:
    repo = Mock()
    repo.favorite_subject_ids.return_value = [2, 7]

    result = FavoritesService(None, repo).status(
        user_id=7,
        subject_type=FavoriteSubjectType.CONSULTANT,
        subject_ids=[7, 2, 7],
    )

    assert result.favorite_subject_ids == [2, 7]
    repo.favorite_subject_ids.assert_called_once_with(
        user_id=7,
        subject_type="consultant",
        subject_ids=[2, 7],
    )
