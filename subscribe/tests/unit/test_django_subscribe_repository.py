# mypy: disable-error-code="no-untyped-def,no-any-return,attr-defined,return-value"
from typing import Any

import pytest

from subscribe.infrastructure.django_repository import DjangoSubscribeRepository


@pytest.fixture
def repo() -> DjangoSubscribeRepository:
    return DjangoSubscribeRepository()


class TestDjangoSubscribeRepository:
    def test_is_subscribed_true(self, mocker: Any, repo: DjangoSubscribeRepository) -> None:
        mock_qs = mocker.Mock()
        mock_qs.exists.return_value = True
        mocker.patch(
            'subscribe.infrastructure.django_repository.Subscribe.objects.filter',
            return_value=mock_qs,
        )

        result = repo.is_subscribed(1, 2)

        assert result is True
        mock_qs.exists.assert_called_once()

    def test_is_subscribed_false(self, mocker: Any, repo: DjangoSubscribeRepository) -> None:
        mock_qs = mocker.Mock()
        mock_qs.exists.return_value = False
        mocker.patch(
            'subscribe.infrastructure.django_repository.Subscribe.objects.filter',
            return_value=mock_qs,
        )

        result = repo.is_subscribed(1, 2)

        assert result is False
        mock_qs.exists.assert_called_once()

    def test_add_calls_create(self, mocker: Any, repo: DjangoSubscribeRepository) -> None:
        mock_create = mocker.patch(
            'subscribe.infrastructure.django_repository.Subscribe.objects.create'
        )

        repo.add(1, 2)

        mock_create.assert_called_once_with(subscribe_from_id=1, subscribe_to_id=2)

    def test_delete_calls_filter_delete(self, mocker: Any, repo: DjangoSubscribeRepository) -> None:
        mock_qs = mocker.Mock()
        mocker.patch(
            'subscribe.infrastructure.django_repository.Subscribe.objects.filter',
            return_value=mock_qs,
        )

        repo.delete(1, 2)

        mock_qs.delete.assert_called_once()

    def test_check_true(self, mocker: Any, repo: DjangoSubscribeRepository) -> None:
        mock_qs = mocker.Mock()
        mock_qs.exists.return_value = True
        mocker.patch(
            'subscribe.infrastructure.django_repository.Subscribe.objects.filter',
            return_value=mock_qs,
        )

        assert repo.check(1, 2) is True

    def test_check_false(self, mocker: Any, repo: DjangoSubscribeRepository) -> None:
        mock_qs = mocker.Mock()
        mock_qs.exists.return_value = False
        mocker.patch(
            'subscribe.infrastructure.django_repository.Subscribe.objects.filter',
            return_value=mock_qs,
        )

        assert repo.check(1, 2) is False

    def test_get_all_returns_list(self, mocker: Any, repo: DjangoSubscribeRepository) -> None:
        mock_user1 = mocker.Mock(id=2, username='user2')
        mock_user2 = mocker.Mock(id=3, username='user3')

        mock_sub1 = mocker.Mock(subscribe_to=mock_user1, subscribe_to_id=2)
        mock_sub2 = mocker.Mock(subscribe_to=mock_user2, subscribe_to_id=3)

        mock_qs = [mock_sub1, mock_sub2]
        mocker.patch(
            'subscribe.infrastructure.django_repository.Subscribe.objects.filter',
            return_value=mocker.Mock(select_related=lambda *args, **kwargs: mock_qs),
        )

        result = repo.get_all(1)

        assert {'to_id': 2, 'username': 'user2'} in result
        assert {'to_id': 3, 'username': 'user3'} in result
        assert len(result) == 2

    def test_get_all_empty(self, mocker: Any, repo: DjangoSubscribeRepository) -> None:
        mocker.patch(
            'subscribe.infrastructure.django_repository.Subscribe.objects.filter',
            return_value=mocker.Mock(select_related=lambda *args, **kwargs: []),
        )

        result = repo.get_all(1)

        assert result == []
