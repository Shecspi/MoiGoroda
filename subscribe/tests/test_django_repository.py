import pytest
from datetime import datetime

from django.http import Http404

from subscribe.infrastructure.django_repository import DjangoNotificationRepository
from subscribe.domain.entities import Notification


@pytest.fixture
def repo():
    return DjangoNotificationRepository()


@pytest.fixture
def mock_notification(mocker):
    """Фейковый ORM-объект VisitedCityNotification"""
    obj = mocker.Mock()
    obj.id = 1
    obj.city_id = 10
    obj.city.title = 'Москва'
    obj.city.region.id = 100
    obj.city.region.full_name = 'ЦФО'
    obj.city.country.code = 'RU'
    obj.city.country.name = 'Россия'
    obj.is_read = False
    obj.sender_id = 200
    obj.sender.username = 'user123'
    obj.read_at = None
    return obj


def test__to_entity(repo, mock_notification):
    entity = repo._to_entity(mock_notification)
    assert isinstance(entity, Notification)
    assert entity.id == mock_notification.id
    assert entity.city_id == mock_notification.city_id
    assert entity.city_title == mock_notification.city.title
    assert entity.region_id == mock_notification.city.region.id
    assert entity.country_code == mock_notification.city.country.code
    assert entity.sender_username == mock_notification.sender.username


def test__to_entity_with_missing_relations(mocker):
    """Фиксируем текущее поведение: если region или country отсутствуют — будет AttributeError"""
    obj = mocker.Mock()
    obj.id = 1
    obj.city_id = 10
    obj.city.title = 'City'
    obj.city.region = None
    obj.city.country = None
    obj.is_read = False
    obj.sender_id = 5
    obj.sender.username = 'sender'
    obj.read_at = None

    repo = DjangoNotificationRepository()
    with pytest.raises(AttributeError):
        repo._to_entity(obj)


def test_list_for_user(repo, mocker, mock_notification):
    qs = [mock_notification]
    mock_filter = mocker.patch(
        'subscribe.infrastructure.django_repository.VisitedCityNotification.objects.filter',
        return_value=mocker.Mock(
            select_related=mocker.Mock(
                return_value=mocker.Mock(order_by=mocker.Mock(return_value=qs))
            )
        ),
    )

    result = repo.list_for_user(user_id=1)
    assert isinstance(result, list)
    assert result[0].id == mock_notification.id
    mock_filter.assert_called_once_with(recipient_id=1)


def test_list_for_user_empty(mocker):
    mocker.patch(
        'subscribe.infrastructure.django_repository.VisitedCityNotification.objects.filter',
        return_value=mocker.Mock(
            select_related=lambda *a, **kw: mocker.Mock(order_by=lambda *a, **kw: [])
        ),
    )
    repo = DjangoNotificationRepository()
    result = repo.list_for_user(user_id=1)
    assert result == []


def test_get_for_user(repo, mocker, mock_notification):
    mock_get_object_or_404 = mocker.patch(
        'subscribe.infrastructure.django_repository.get_object_or_404',
        return_value=mock_notification,
    )

    result = repo.get_for_user(user_id=1, notification_id=1)
    assert isinstance(result, Notification)
    assert result.id == mock_notification.id
    mock_get_object_or_404.assert_called_once()


def test_get_for_user_not_found(mocker):
    mocker.patch(
        'subscribe.infrastructure.django_repository.get_object_or_404',
        side_effect=Http404,
    )
    repo = DjangoNotificationRepository()
    with pytest.raises(Http404):
        repo.get_for_user(user_id=1, notification_id=42)


def test_delete(repo, mocker, mock_notification):
    mock_get_object_or_404 = mocker.patch(
        'subscribe.infrastructure.django_repository.get_object_or_404',
        return_value=mock_notification,
    )

    repo.delete(user_id=1, notification_id=1)

    mock_get_object_or_404.assert_called_once()
    mock_notification.delete.assert_called_once()


def test_delete_not_found(mocker):
    mocker.patch(
        'subscribe.infrastructure.django_repository.get_object_or_404',
        side_effect=Http404,
    )
    repo = DjangoNotificationRepository()
    with pytest.raises(Http404):
        repo.delete(user_id=1, notification_id=42)


def test_update_read_status(repo, mocker, mock_notification):
    mock_get = mocker.patch(
        'subscribe.infrastructure.django_repository.VisitedCityNotification.objects.get',
        return_value=mock_notification,
    )

    notification = Notification(
        id=1,
        city_id=10,
        city_title='Москва',
        region_id=100,
        region_title='ЦФО',
        country_code='RU',
        country_title='Россия',
        is_read=True,
        sender_id=200,
        sender_username='user123',
        read_at=datetime(2024, 1, 1),
    )

    repo.update_read_status(notification)

    mock_get.assert_called_once_with(pk=1)
    assert mock_notification.read_at == notification.read_at
    assert mock_notification.is_read is True
    mock_notification.save.assert_called_once_with(update_fields=['read_at', 'is_read'])


def test_update_read_status_not_found(mocker):
    mocker.patch(
        'subscribe.infrastructure.django_repository.VisitedCityNotification.objects.get',
        side_effect=Exception('not found'),
    )
    repo = DjangoNotificationRepository()
    notification = Notification(
        id=123,
        city_id=1,
        city_title='City',
        region_id=1,
        region_title='Region',
        country_code='RU',
        country_title='Russia',
        is_read=True,
        sender_id=2,
        sender_username='test',
    )
    with pytest.raises(Exception, match='not found'):
        repo.update_read_status(notification)


def test_update_read_status_unread(mocker):
    mock_obj = mocker.Mock()
    mocker.patch(
        'subscribe.infrastructure.django_repository.VisitedCityNotification.objects.get',
        return_value=mock_obj,
    )

    repo = DjangoNotificationRepository()
    notification = Notification(
        id=123,
        city_id=1,
        city_title='City',
        region_id=1,
        region_title='Region',
        country_code='RU',
        country_title='Russia',
        is_read=False,
        sender_id=2,
        sender_username='test',
        read_at=None,
    )
    repo.update_read_status(notification)

    assert mock_obj.is_read is False
    assert mock_obj.read_at is None
    mock_obj.save.assert_called_once_with(update_fields=['read_at', 'is_read'])
