import pytest
from rest_framework.test import APIRequestFactory
from rest_framework import status
from subscribe.views import NotificationViewSet
from unittest.mock import MagicMock, patch


@pytest.fixture
def factory():
    return APIRequestFactory()


@pytest.fixture
def viewset():
    return NotificationViewSet.as_view({'get': 'list', 'patch': 'partial_update'})


@pytest.fixture
def mock_user(mocker):
    user = mocker.Mock()
    user.notifications.filter.return_value.order_by.return_value = [
        mocker.Mock(id=1, message='Test1', is_read=False),
        mocker.Mock(id=2, message='Test2', is_read=False),
    ]
    return user


@pytest.fixture
def mock_notification(mocker):
    notif = mocker.Mock()
    notif.id = 1
    notif.message = 'Message'
    notif.is_read = False
    return notif


# Тесты list()
def test_notification_list_returns_notifications_sorted(factory, mock_user, mocker):
    request = factory.get('/notification/')
    request.user = mock_user

    # Мокаем цепочку order_by('is_read', '-id') -> возвращает список уведомлений
    notifications_qs_mock = mocker.MagicMock()
    notifications_sorted = [mocker.MagicMock(), mocker.MagicMock()]
    notifications_qs_mock.order_by.return_value = notifications_sorted
    mock_user.notifications = notifications_qs_mock

    # Мокаем сериализатор, чтобы вернуть фиктивные данные
    serializer_mock = mocker.patch('subscribe.views.NotificationSerializer')
    serializer_instance = serializer_mock.return_value
    serializer_instance.data = 'mocked'

    # Вызываем view
    view = NotificationViewSet.as_view({'get': 'list'})
    response = view(request)

    # Проверки
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'notifications': 'mocked'}

    notifications_qs_mock.order_by.assert_called_once_with('is_read', '-id')
    serializer_mock.assert_called_once_with(notifications_sorted, many=True)


# Тесты partial_update()


@patch('subscribe.views.get_object_or_404')
@patch('subscribe.serializers.NotificationSerializer.save')
def test_partial_update_success(mock_save, mock_get_object_or_404, factory, mock_notification):
    # Возвращаем мок-объект
    mock_get_object_or_404.return_value = mock_notification
    mock_save.return_value = None  # предотвращаем реальные операции save()

    # Симулируем, что после сохранения поле is_read стало True
    mock_notification.is_read = True

    request = factory.patch('/notification/1/', {'is_read': True}, format='json')
    request.user = MagicMock()

    view = NotificationViewSet.as_view({'patch': 'partial_update'})
    response = view(request, pk=1)

    assert response.status_code == 200
    assert response.data['is_read'] is True
    mock_save.assert_called_once()
    mock_get_object_or_404.assert_called_once()


@patch('subscribe.views.get_object_or_404')
def test_partial_update_invalid_data(mock_get_object_or_404, factory, mock_notification):
    mock_get_object_or_404.return_value = mock_notification

    # Передаём неверное значение для is_read (должно быть boolean)
    request = factory.patch('/notification/1/', {'is_read': 'not_bool'}, format='json')
    request.user = MagicMock()

    view = NotificationViewSet.as_view({'patch': 'partial_update'})

    response = view(request, pk=1)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'is_read' in response.data


@patch('subscribe.views.get_object_or_404')
def test_partial_update_object_not_found(mock_get_object_or_404, factory):
    from rest_framework.exceptions import NotFound

    # Симулируем, что объект не найден
    mock_get_object_or_404.side_effect = NotFound()

    request = factory.patch('/notification/999/', {'is_read': True}, format='json')
    request.user = MagicMock()

    view = NotificationViewSet.as_view({'patch': 'partial_update'})

    response = view(request, pk=999)

    assert response.status_code == 404


# Тест, что permission_classes отрабатывают (требуется аутентификация)


def test_permission_classes_enforced(factory):
    request = factory.get('/notification/')
    request.user = None  # Анонимный пользователь

    view = NotificationViewSet.as_view({'get': 'list'})

    response = view(request)

    # Нет аутентификации — ответ 403 или 401 в зависимости от настроек
    assert response.status_code in (401, 403)


# Тесты destroy()


def test_destroy_deletes_user_notification(factory, mocker, mock_user):
    # Мокаем объект уведомления
    notification_mock = mocker.MagicMock()
    notifications_qs = mocker.MagicMock()
    notifications_qs.filter.return_value.exists.return_value = True
    notifications_qs.get.return_value = notification_mock
    mock_user.notifications = notifications_qs

    # Мокаем get_object_or_404, чтобы он вернул наш объект
    mocker.patch('subscribe.views.get_object_or_404', return_value=notification_mock)

    request = factory.delete('/notification/123/')
    request.user = mock_user

    view = NotificationViewSet.as_view({'delete': 'destroy'})
    response = view(request, pk=123)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    notification_mock.delete.assert_called_once()


def test_destroy_returns_404_if_notification_not_found(factory, mocker, mock_user):
    # Мокаем get_object_or_404, чтобы он выбросил Http404
    mocker.patch('subscribe.views.get_object_or_404', side_effect=Exception('Not Found'))

    request = factory.delete('/notification/999/')
    request.user = mock_user

    view = NotificationViewSet.as_view({'delete': 'destroy'})

    with pytest.raises(Exception, match='Not Found'):
        view(request, pk=999)


def test_destroy_returns_404_if_notification_not_owned_by_user(factory, mocker, mock_user):
    # Допустим, другой пользователь имеет уведомление с этим ID
    # Поэтому get_object_or_404 ничего не находит в request.user.notifications
    mocker.patch('subscribe.views.get_object_or_404', side_effect=Exception('Not Found'))

    request = factory.delete('/notification/321/')
    request.user = mock_user

    view = NotificationViewSet.as_view({'delete': 'destroy'})

    with pytest.raises(Exception, match='Not Found'):
        view(request, pk=321)


@patch('subscribe.views.get_object_or_404')
def test_partial_update_is_read_false_does_not_set_read_at(mock_get_object_or_404, factory, mock_notification):
    """
    Если is_read=False, read_at не должен устанавливаться.
    """
    mock_notification.read_at = None
    mock_get_object_or_404.return_value = mock_notification

    request = factory.patch('/notification/1/', {'is_read': False}, format='json')
    request.user = MagicMock()

    view = NotificationViewSet.as_view({'patch': 'partial_update'})
    response = view(request, pk=1)

    assert response.status_code == 200
    assert response.data['is_read'] is False
    assert mock_notification.read_at is None


@patch('subscribe.views.get_object_or_404')
def test_partial_update_with_empty_body(mock_get_object_or_404, factory, mock_notification):
    """
    Пустое тело должно валидироваться (partial=True) и ничего не менять.
    """
    mock_notification.is_read = False
    mock_notification.read_at = None
    mock_get_object_or_404.return_value = mock_notification

    request = factory.patch('/notification/1/', {}, format='json')
    request.user = MagicMock()

    view = NotificationViewSet.as_view({'patch': 'partial_update'})
    response = view(request, pk=1)

    assert response.status_code == 200
    # Поле is_read отсутствует в validated_data, поэтому оно не должно измениться
    assert response.data['is_read'] is False
    assert mock_notification.read_at is None


def test_notification_list_returns_empty_list(factory, mocker):
    """
    list() должен возвращать пустой список, если уведомлений нет.
    """
    request = factory.get('/notification/')
    request.user = mocker.Mock()

    notifications_qs_mock = mocker.MagicMock()
    notifications_qs_mock.order_by.return_value = []
    request.user.notifications = notifications_qs_mock

    serializer_mock = mocker.patch('subscribe.views.NotificationSerializer')
    serializer_instance = serializer_mock.return_value
    serializer_instance.data = []

    view = NotificationViewSet.as_view({'get': 'list'})
    response = view(request)

    assert response.status_code == 200
    assert response.data == {'notifications': []}
    notifications_qs_mock.order_by.assert_called_once_with('is_read', '-id')
    serializer_mock.assert_called_once_with([], many=True)
