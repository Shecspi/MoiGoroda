import pytest
from django.core.exceptions import ObjectDoesNotExist

from account.models import ShareSettings
from subscribe.infrastructure.django_repository import DjangoShareSettingsRepository


@pytest.fixture
def repository():
    return DjangoShareSettingsRepository()


def test_can_subscribe_returns_true_if_record_exists(mocker, repository):
    mock_obj = mocker.Mock(spec=ShareSettings)
    mock_obj.can_subscribe = True
    mocker.patch.object(ShareSettings.objects, "get", return_value=mock_obj)

    result = repository.can_subscribe(user_id=1)

    assert result is True
    ShareSettings.objects.get.assert_called_once_with(user_id=1)


def test_can_subscribe_returns_false_if_record_exists_with_false(mocker, repository):
    mock_obj = mocker.Mock(spec=ShareSettings)
    mock_obj.can_subscribe = False
    mocker.patch.object(ShareSettings.objects, "get", return_value=mock_obj)

    result = repository.can_subscribe(user_id=2)

    assert result is False
    ShareSettings.objects.get.assert_called_once_with(user_id=2)


def test_can_subscribe_returns_false_if_record_does_not_exist(mocker, repository):
    mocker.patch.object(
        ShareSettings.objects, "get", side_effect=ShareSettings.DoesNotExist
    )

    result = repository.can_subscribe(user_id=3)

    assert result is False
    ShareSettings.objects.get.assert_called_once_with(user_id=3)
