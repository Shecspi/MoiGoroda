# mypy: disable-error-code="no-untyped-def,no-any-return,attr-defined,return-value,assignment"
from typing import Any
from datetime import datetime

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth.models import AnonymousUser, User

from subscribe.domain.entities import Notification
from subscribe.api.views import NotificationViewSet


# Фейковый сервис для тестирования
class FakeService:
    def __init__(self, notifications=None) -> None:
        self.notifications = notifications or []
        self.deleted: list[int] = []
        self.read_updates: list[Any] = []

    def list_notifications(self, user_id) -> None:
        return self.notifications

    def mark_notification_as_read(self, user_id, notification_id) -> None:
        notif = next(n for n in self.notifications if n.id == notification_id)
        if not notif.read_at:
            notif.read_at = datetime(2025, 8, 16)
            notif.is_read = True
            self.read_updates.append(notif)
        return notif

    def delete_notification(self, user_id, notification_id) -> None:
        self.deleted.append(notification_id)
        self.notifications = [n for n in self.notifications if n.id != notification_id]


@pytest.fixture
def user(db) -> None:
    return User.objects.create_user(username='testuser', password='123')


@pytest.fixture
def notifications() -> None:
    return [
        Notification(
            id=1,
            city_id=10,
            city_title='CityA',
            region_id=100,
            region_title='RegionA',
            country_code='RU',
            country_title='Russia',
            is_read=False,
            sender_id=5,
            sender_username='sender1',
        ),
        Notification(
            id=2,
            city_id=20,
            city_title='CityB',
            region_id=200,
            region_title='RegionB',
            country_code='US',
            country_title='USA',
            is_read=True,
            sender_id=6,
            sender_username='sender2',
            read_at=datetime(2025, 8, 15),
        ),
    ]


@pytest.fixture
def viewset(notifications) -> None:
    class TestViewSet(NotificationViewSet):
        service_class = lambda self: FakeService(notifications=list(notifications))  # noqa: E731  # type: ignore[assignment]

    return TestViewSet.as_view(
        {
            'get': 'list',
            'patch': 'partial_update',
            'delete': 'destroy',
        }
    )


def test_list_notifications(user, notifications) -> None:
    factory = APIRequestFactory()
    request = factory.get('/notifications/')
    force_authenticate(request, user=user)

    class TestViewSet(NotificationViewSet):
        service_class = lambda self: FakeService(notifications=list(notifications))  # noqa: E731  # type: ignore[assignment]

    response = TestViewSet.as_view({'get': 'list'})(request)
    assert response.status_code == status.HTTP_200_OK
    assert 'notifications' in response.data
    assert len(response.data['notifications']) == len(notifications)


def test_mark_notification_as_read(user, notifications) -> None:
    factory = APIRequestFactory()
    request = factory.patch('/notifications/1/')
    force_authenticate(request, user=user)

    class TestViewSet(NotificationViewSet):
        service_class = lambda self: FakeService(notifications=list(notifications))  # noqa: E731  # type: ignore[assignment]

    response = TestViewSet.as_view({'patch': 'partial_update'})(request, pk=1)
    assert response.status_code == status.HTTP_200_OK
    notif = response.data
    assert notif['id'] == 1
    assert notif['is_read'] is True
    assert notif['read_at'] is not None

    # Проверка, что другие поля не изменились
    orig = next(n for n in notifications if n.id == 1)
    assert notif['city_id'] == orig.city_id
    assert notif['city_title'] == orig.city_title


def test_delete_notification(user, notifications) -> None:
    factory = APIRequestFactory()
    request = factory.delete('/notifications/1/')
    force_authenticate(request, user=user)

    class TestViewSet(NotificationViewSet):
        service_class = lambda self: FakeService(notifications=list(notifications))  # noqa: E731  # type: ignore[assignment]

    response = TestViewSet.as_view({'delete': 'destroy'})(request, pk=1)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_permission_classes_enforced() -> None:
    factory = APIRequestFactory()
    request = factory.get('/notifications/')
    request.user = AnonymousUser()

    class TestViewSet(NotificationViewSet):
        service_class = lambda self: FakeService()  # noqa: E731  # type: ignore[assignment]

    response = TestViewSet.as_view({'get': 'list'})(request)
    assert response.status_code == status.HTTP_403_FORBIDDEN
