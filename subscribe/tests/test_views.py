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
