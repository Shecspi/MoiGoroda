import pytest
from datetime import datetime
from subscribe.domain.entities import Notification
from subscribe.application.services import NotificationService


@pytest.fixture
def mock_repo(mocker):
    """Мокаем репозиторий."""
    return mocker.Mock()


@pytest.fixture
def service(mock_repo):
    """Сервис с замоканным репозиторием."""
    return NotificationService(repo=mock_repo)


@pytest.fixture
def sample_notification():
    """Пример уведомления."""
    return Notification(
        id=1,
        city_id=10,
        city_title='Москва',
        region_id=20,
        region_title='Московская область',
        country_code='RU',
        country_title='Россия',
        is_read=False,
        sender_id=2,
        sender_username='testuser',
        read_at=None,
    )


def test_list_notifications(service, mock_repo, sample_notification):
    """Сервис должен возвращать список уведомлений из репозитория."""
    mock_repo.list_for_user.return_value = [sample_notification]

    result = service.list_notifications(user_id=1)

    assert result == [sample_notification]
    mock_repo.list_for_user.assert_called_once_with(1)


def test_mark_notification_as_read_when_unread(service, mock_repo, sample_notification):
    """Если уведомление не прочитано, оно должно стать прочитанным."""
    mock_repo.get_for_user.return_value = sample_notification

    result = service.mark_notification_as_read(user_id=1, notification_id=1)

    assert result.is_read is True
    assert result.read_at is not None
    mock_repo.get_for_user.assert_called_once_with(1, 1)
    mock_repo.update_read_status.assert_called_once_with(sample_notification)


def test_mark_notification_as_read_only_updates_read_fields(
    service, mock_repo, sample_notification
):
    """Проверяем, что обновляются только is_read и read_at."""
    mock_repo.get_for_user.return_value = sample_notification
    original = sample_notification.__dict__.copy()

    service.mark_notification_as_read(user_id=1, notification_id=1)

    # проверяем, что остальные поля не изменились
    for field in original:
        if field not in ('is_read', 'read_at'):
            assert getattr(sample_notification, field) == original[field]


def test_mark_notification_as_read_when_already_read(service, mock_repo, sample_notification):
    """Если уведомление уже прочитано, повторно обновлять не нужно."""
    sample_notification.is_read = True
    sample_notification.read_at = datetime(2024, 1, 1)
    mock_repo.get_for_user.return_value = sample_notification

    result = service.mark_notification_as_read(user_id=1, notification_id=1)

    assert result.is_read is True
    assert result.read_at == datetime(2024, 1, 1)
    mock_repo.get_for_user.assert_called_once_with(1, 1)
    mock_repo.update_read_status.assert_not_called()


def test_delete_notification(service, mock_repo):
    """Сервис должен удалять уведомление через репозиторий."""
    service.delete_notification(user_id=1, notification_id=1)

    mock_repo.delete.assert_called_once_with(1, 1)
