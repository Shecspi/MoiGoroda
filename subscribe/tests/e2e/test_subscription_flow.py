"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import json
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from account.models import ShareSettings
from subscribe.infrastructure.models import Subscribe, VisitedCityNotification


@pytest.mark.e2e
@pytest.mark.django_db
def test_complete_subscription_workflow(client: Client) -> None:
    """E2E тест полного цикла подписки: подписка -> проверка -> отписка"""
    # Создаём пользователей
    user1 = User.objects.create_user(username='user1', password='password1')
    user2 = User.objects.create_user(username='user2', password='password2')

    # Разрешаем подписку на user2
    ShareSettings.objects.create(
        user=user2,
        can_share_dashboard=True,
        can_share_city_map=True,
        can_share_region_map=True,
        can_subscribe=True,
    )

    # Авторизуемся как user1
    client.login(username='user1', password='password1')

    # Шаг 1: Подписываемся на user2
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': user1.id, 'to_id': user2.id, 'action': 'subscribe'}),
        content_type='application/json',
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'subscribed'

    # Проверяем что подписка создана
    assert Subscribe.objects.filter(subscribe_from=user1, subscribe_to=user2).exists()

    # Шаг 2: Проверяем идемпотентность - повторная подписка не создаёт дубликат
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': user1.id, 'to_id': user2.id, 'action': 'subscribe'}),
        content_type='application/json',
    )
    assert response.status_code == 200
    assert Subscribe.objects.filter(subscribe_from=user1, subscribe_to=user2).count() == 1

    # Шаг 3: Отписываемся
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': user1.id, 'to_id': user2.id, 'action': 'unsubscribe'}),
        content_type='application/json',
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'unsubscribed'

    # Проверяем что подписка удалена
    assert not Subscribe.objects.filter(subscribe_from=user1, subscribe_to=user2).exists()


@pytest.mark.e2e
@pytest.mark.django_db
def test_notification_workflow(
    client: Client, test_country: Any, test_region_type: Any, test_region: Any, test_city: Any
) -> None:
    """E2E тест полного цикла уведомлений: создание -> чтение -> удаление"""
    # Создаём пользователей
    sender = User.objects.create_user(username='sender', password='password1')
    recipient = User.objects.create_user(username='recipient', password='password2')

    # Создаём уведомление
    notification = VisitedCityNotification.objects.create(
        recipient=recipient, sender=sender, city=test_city, is_read=False
    )

    # Авторизуемся как получатель
    client.login(username='recipient', password='password2')

    # Шаг 1: Получаем список уведомлений
    response = client.get(reverse('notification-list'))
    assert response.status_code == 200
    data = response.json()
    assert 'notifications' in data
    assert len(data['notifications']) == 1
    assert data['notifications'][0]['id'] == notification.id
    assert data['notifications'][0]['is_read'] is False

    # Шаг 2: Помечаем уведомление как прочитанное
    response = client.patch(reverse('notification-detail', kwargs={'pk': notification.id}))
    assert response.status_code == 200
    data = response.json()
    assert data['is_read'] is True
    assert data['read_at'] is not None

    # Проверяем что статус обновился в БД
    notification.refresh_from_db()
    assert notification.is_read is True
    assert notification.read_at is not None

    # Шаг 3: Удаляем уведомление
    response = client.delete(reverse('notification-detail', kwargs={'pk': notification.id}))
    assert response.status_code == 204

    # Проверяем что уведомление удалено
    assert not VisitedCityNotification.objects.filter(id=notification.id).exists()


@pytest.mark.e2e
@pytest.mark.django_db
def test_subscriber_removal_workflow(client: Client) -> None:
    """E2E тест удаления подписчика владельцем аккаунта"""
    # Создаём пользователей
    user1 = User.objects.create_user(username='user1', password='password1')
    user2 = User.objects.create_user(username='user2', password='password2')

    ShareSettings.objects.create(
        user=user2,
        can_share_dashboard=True,
        can_share_city_map=True,
        can_share_region_map=True,
        can_subscribe=True,
    )

    # user1 подписывается на user2
    Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

    # Авторизуемся как user2 (владелец аккаунта)
    client.login(username='user2', password='password2')

    # Удаляем подписчика
    response = client.post(
        reverse('delete_subscribe'),
        data=json.dumps({'user_id': user1.id}),
        content_type='application/json',
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'success'

    # Проверяем что подписка удалена
    assert not Subscribe.objects.filter(subscribe_from=user1, subscribe_to=user2).exists()


@pytest.mark.e2e
@pytest.mark.django_db
def test_multiple_subscriptions_workflow(client: Client) -> None:
    """E2E тест работы с несколькими подписками"""
    # Создаём несколько пользователей
    user1 = User.objects.create_user(username='user1', password='password1')
    users = [
        User.objects.create_user(username=f'user{i}', password=f'password{i}') for i in range(2, 5)
    ]

    # Разрешаем подписку на всех пользователей
    for user in users:
        ShareSettings.objects.create(
            user=user,
            can_share_dashboard=True,
            can_share_city_map=True,
            can_share_region_map=True,
            can_subscribe=True,
        )

    # Авторизуемся как user1
    client.login(username='user1', password='password1')

    # Подписываемся на всех пользователей
    for user in users:
        response = client.post(
            reverse('save_subscribe'),
            data=json.dumps({'from_id': user1.id, 'to_id': user.id, 'action': 'subscribe'}),
            content_type='application/json',
        )
        assert response.status_code == 200

    # Проверяем что создано 3 подписки
    assert Subscribe.objects.filter(subscribe_from=user1).count() == 3

    # Отписываемся от одного пользователя
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': user1.id, 'to_id': users[0].id, 'action': 'unsubscribe'}),
        content_type='application/json',
    )
    assert response.status_code == 200

    # Проверяем что осталось 2 подписки
    assert Subscribe.objects.filter(subscribe_from=user1).count() == 2
    assert not Subscribe.objects.filter(subscribe_from=user1, subscribe_to=users[0]).exists()


@pytest.mark.e2e
@pytest.mark.django_db
def test_notification_isolation_between_users(
    client: Client, test_country: Any, test_region_type: Any, test_region: Any, test_city: Any
) -> None:
    """E2E тест изоляции уведомлений между пользователями"""
    # Создаём пользователей
    user1 = User.objects.create_user(username='user1', password='password1')
    user2 = User.objects.create_user(username='user2', password='password2')
    user3 = User.objects.create_user(username='user3', password='password3')

    # Создаём уведомления для разных пользователей
    notif1 = VisitedCityNotification.objects.create(
        recipient=user1, sender=user3, city=test_city, is_read=False
    )
    notif2 = VisitedCityNotification.objects.create(
        recipient=user2, sender=user3, city=test_city, is_read=False
    )

    # Авторизуемся как user1
    client.login(username='user1', password='password1')

    # Получаем уведомления - должно быть только одно
    response = client.get(reverse('notification-list'))
    assert response.status_code == 200
    data = response.json()
    assert len(data['notifications']) == 1
    assert data['notifications'][0]['id'] == notif1.id

    # Пытаемся пометить чужое уведомление как прочитанное - должна быть ошибка
    response = client.patch(reverse('notification-detail', kwargs={'pk': notif2.id}))
    assert response.status_code == 404

    # Пытаемся удалить чужое уведомление - должна быть ошибка
    response = client.delete(reverse('notification-detail', kwargs={'pk': notif2.id}))
    assert response.status_code == 404

    # Проверяем что чужое уведомление не удалено
    assert VisitedCityNotification.objects.filter(id=notif2.id).exists()


@pytest.mark.e2e
@pytest.mark.django_db
def test_subscription_permission_changes(client: Client) -> None:
    """E2E тест изменения прав доступа к подписке"""
    # Создаём пользователей
    user1 = User.objects.create_user(username='user1', password='password1')
    user2 = User.objects.create_user(username='user2', password='password2')

    # Разрешаем подписку
    settings = ShareSettings.objects.create(
        user=user2,
        can_share_dashboard=True,
        can_share_city_map=True,
        can_share_region_map=True,
        can_subscribe=True,
    )

    client.login(username='user1', password='password1')

    # Подписываемся успешно
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': user1.id, 'to_id': user2.id, 'action': 'subscribe'}),
        content_type='application/json',
    )
    assert response.status_code == 200

    # Отписываемся
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': user1.id, 'to_id': user2.id, 'action': 'unsubscribe'}),
        content_type='application/json',
    )
    assert response.status_code == 200

    # user2 запрещает подписку
    settings.can_subscribe = False
    settings.save()

    # Пытаемся подписаться снова - теперь должна быть ошибка
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': user1.id, 'to_id': user2.id, 'action': 'subscribe'}),
        content_type='application/json',
    )
    assert response.status_code == 403
    assert 'не разрешил подписываться' in response.json()['message']
