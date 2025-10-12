"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from unittest.mock import patch
from django.urls import reverse

from account.models import ShareSettings
from subscribe.infrastructure.models import Subscribe


# ===== E2E тесты для подписок =====


@pytest.mark.e2e
@pytest.mark.django_db
def test_subscribe_and_view_in_profile_flow(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Создание двух пользователей -> Подписка -> Просмотр подписки в профиле
    """
    # Шаг 1: Создаём двух пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    # Шаг 2: Логинимся как user1
    client.force_login(user1)

    # Шаг 3: Создаём подписку от user1 на user2
    Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

    # Шаг 4: Открываем профиль user1 и проверяем подписки
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    assert response.context['number_of_subscribed_users'] == 1
    assert response.context['number_of_subscriber_users'] == 0

    subscribed_users = response.context['subscribed_users']
    assert len(subscribed_users) == 1
    assert subscribed_users[0].username == 'user2'

    # Шаг 5: Логинимся как user2 и проверяем подписчиков
    client.force_login(user2)
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    assert response.context['number_of_subscribed_users'] == 0
    assert response.context['number_of_subscriber_users'] == 1

    subscriber_users = response.context['subscriber_users']
    assert len(subscriber_users) == 1
    assert subscriber_users[0].username == 'user1'


@pytest.mark.e2e
@pytest.mark.django_db
def test_mutual_subscriptions_flow(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Взаимные подписки двух пользователей
    """
    # Шаг 1: Создаём двух пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    # Шаг 2: Создаём взаимные подписки
    Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)
    Subscribe.objects.create(subscribe_from=user2, subscribe_to=user1)

    # Шаг 3: Проверяем профиль user1
    client.force_login(user1)
    response = client.get(reverse('profile'))

    assert response.context['number_of_subscribed_users'] == 1  # Подписан на user2
    assert response.context['number_of_subscriber_users'] == 1  # user2 подписан на него

    # Шаг 4: Проверяем профиль user2
    client.force_login(user2)
    response = client.get(reverse('profile'))

    assert response.context['number_of_subscribed_users'] == 1  # Подписан на user1
    assert response.context['number_of_subscriber_users'] == 1  # user1 подписан на него


@pytest.mark.e2e
@pytest.mark.django_db
def test_subscription_with_share_settings_flow(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Подписка -> Настройка публикации подписчиком -> Проверка can_subscribe
    """
    # Шаг 1: Создаём двух пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    # Шаг 2: user2 подписывается на user1
    Subscribe.objects.create(subscribe_from=user2, subscribe_to=user1)

    # Шаг 3: Проверяем профиль user1 (can_subscribe должен быть False по умолчанию)
    client.force_login(user1)
    response = client.get(reverse('profile'))

    subscriber_users = response.context['subscriber_users']
    assert len(subscriber_users) == 1
    assert subscriber_users[0].username == 'user2'
    assert subscriber_users[0].can_subscribe is False

    # Шаг 4: user2 настраивает публикацию статистики
    client.force_login(user2)
    ShareSettings.objects.create(user=user2, can_share=True)

    # Шаг 5: Проверяем профиль user1 снова (can_subscribe должен быть True)
    client.force_login(user1)
    response = client.get(reverse('profile'))

    subscriber_users = response.context['subscriber_users']
    assert subscriber_users[0].can_subscribe is True


@pytest.mark.e2e
@pytest.mark.django_db
def test_multiple_subscriptions_flow(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Один пользователь подписывается на нескольких
    """
    # Шаг 1: Создаём четырёх пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    user3 = django_user_model.objects.create_user(username='user3', password='password123')
    user4 = django_user_model.objects.create_user(username='user4', password='password123')

    # Шаг 2: user1 подписывается на всех остальных
    Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)
    Subscribe.objects.create(subscribe_from=user1, subscribe_to=user3)
    Subscribe.objects.create(subscribe_from=user1, subscribe_to=user4)

    # Шаг 3: Проверяем профиль user1
    client.force_login(user1)
    response = client.get(reverse('profile'))

    assert response.context['number_of_subscribed_users'] == 3
    subscribed_usernames = {user.username for user in response.context['subscribed_users']}
    assert subscribed_usernames == {'user2', 'user3', 'user4'}

    # Шаг 4: Проверяем профиль user2 (должен видеть user1 как подписчика)
    client.force_login(user2)
    response = client.get(reverse('profile'))

    assert response.context['number_of_subscriber_users'] == 1
    assert response.context['subscriber_users'][0].username == 'user1'


@pytest.mark.e2e
@pytest.mark.django_db
def test_subscription_deletion_flow(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Создание подписки -> Удаление подписки -> Проверка
    """
    # Шаг 1: Создаём двух пользователей и подписку
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    subscription = Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

    # Шаг 2: Проверяем, что подписка есть
    client.force_login(user1)
    response = client.get(reverse('profile'))
    assert response.context['number_of_subscribed_users'] == 1

    # Шаг 3: Удаляем подписку
    subscription.delete()

    # Шаг 4: Проверяем, что подписки нет
    response = client.get(reverse('profile'))
    assert response.context['number_of_subscribed_users'] == 0


@pytest.mark.e2e
@pytest.mark.django_db
def test_subscription_with_mixed_share_settings_flow(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Несколько подписчиков с разными настройками публикации
    """
    # Шаг 1: Создаём пользователей
    main_user = django_user_model.objects.create_user(username='mainuser', password='password123')
    subscriber1 = django_user_model.objects.create_user(username='sub1', password='password123')
    subscriber2 = django_user_model.objects.create_user(username='sub2', password='password123')
    subscriber3 = django_user_model.objects.create_user(username='sub3', password='password123')

    # Шаг 2: Все подписываются на main_user
    Subscribe.objects.create(subscribe_from=subscriber1, subscribe_to=main_user)
    Subscribe.objects.create(subscribe_from=subscriber2, subscribe_to=main_user)
    Subscribe.objects.create(subscribe_from=subscriber3, subscribe_to=main_user)

    # Шаг 3: Настраиваем публикацию для subscriber1 и subscriber3
    ShareSettings.objects.create(user=subscriber1, can_share=True)
    ShareSettings.objects.create(user=subscriber3, can_share=False)

    # Шаг 4: Проверяем профиль main_user
    client.force_login(main_user)
    response = client.get(reverse('profile'))

    assert response.context['number_of_subscriber_users'] == 3

    subscriber_users = response.context['subscriber_users']
    sub1_data = next(s for s in subscriber_users if s.username == 'sub1')
    sub2_data = next(s for s in subscriber_users if s.username == 'sub2')
    sub3_data = next(s for s in subscriber_users if s.username == 'sub3')

    assert sub1_data.can_subscribe is True
    assert sub2_data.can_subscribe is False  # Нет настроек
    assert sub3_data.can_subscribe is False  # can_share=False


@pytest.mark.e2e
@pytest.mark.django_db
def test_subscription_visibility_after_profile_update(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Подписка -> Обновление профиля -> Подписка всё ещё видна
    """
    # Шаг 1: Создаём пользователей и подписку
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

    # Шаг 2: Проверяем подписку
    client.force_login(user1)
    response = client.get(reverse('profile'))
    assert response.context['number_of_subscribed_users'] == 1

    # Шаг 3: Обновляем профиль
    with patch('account.views.profile.logger'):
        client.post(
            reverse('profile'),
            data={
                'username': 'user1',
                'email': 'newemail@example.com',
                'first_name': 'Test',
                'last_name': 'User',
            },
        )

    # Шаг 4: Проверяем, что подписка всё ещё есть
    response = client.get(reverse('profile'))
    assert response.context['number_of_subscribed_users'] == 1
    assert response.context['subscribed_users'][0].username == 'user2'


@pytest.mark.e2e
@pytest.mark.django_db
def test_subscription_chain_flow(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Цепочка подписок A -> B -> C -> A
    """
    # Шаг 1: Создаём трёх пользователей
    userA = django_user_model.objects.create_user(username='userA', password='password123')
    userB = django_user_model.objects.create_user(username='userB', password='password123')
    userC = django_user_model.objects.create_user(username='userC', password='password123')

    # Шаг 2: Создаём цепочку подписок
    Subscribe.objects.create(subscribe_from=userA, subscribe_to=userB)
    Subscribe.objects.create(subscribe_from=userB, subscribe_to=userC)
    Subscribe.objects.create(subscribe_from=userC, subscribe_to=userA)

    # Шаг 3: Проверяем профиль userA
    client.force_login(userA)
    response = client.get(reverse('profile'))

    assert response.context['number_of_subscribed_users'] == 1  # Подписан на B
    assert response.context['subscribed_users'][0].username == 'userB'
    assert response.context['number_of_subscriber_users'] == 1  # C подписан на него
    assert response.context['subscriber_users'][0].username == 'userC'

    # Шаг 4: Проверяем профиль userB
    client.force_login(userB)
    response = client.get(reverse('profile'))

    assert response.context['number_of_subscribed_users'] == 1  # Подписан на C
    assert response.context['subscribed_users'][0].username == 'userC'
    assert response.context['number_of_subscriber_users'] == 1  # A подписан на него
    assert response.context['subscriber_users'][0].username == 'userA'


@pytest.mark.e2e
@pytest.mark.django_db
def test_no_subscriptions_shows_zero_counts(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Пользователь без подписок видит нули в профиле
    """
    # Шаг 1: Создаём пользователя без подписок
    user = django_user_model.objects.create_user(username='lonelyuser', password='password123')

    # Шаг 2: Логинимся и открываем профиль
    client.force_login(user)
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    assert response.context['number_of_subscribed_users'] == 0
    assert response.context['number_of_subscriber_users'] == 0
    assert len(response.context['subscribed_users']) == 0
    assert len(response.context['subscriber_users']) == 0


@pytest.mark.e2e
@pytest.mark.django_db
def test_complete_subscription_lifecycle(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Полный жизненный цикл подписки
    Регистрация -> Подписка -> Настройка публикации -> Проверка -> Отписка
    """
    # Шаг 1: Регистрируем двух пользователей
    with patch('account.views.access.logger_email'):
        # Первый пользователь
        client.post(
            reverse('signup'),
            data={
                'username': 'alice',
                'email': 'alice@example.com',
                'password1': 'AlicePass123!',
                'password2': 'AlicePass123!',
                'personal_data_consent': True,
                'personal_data_version': '1.0',
            },
            follow=True,
        )
        client.post(reverse('logout'))

        # Второй пользователь
        client.post(
            reverse('signup'),
            data={
                'username': 'bob',
                'email': 'bob@example.com',
                'password1': 'BobPass123!',
                'password2': 'BobPass123!',
                'personal_data_consent': True,
                'personal_data_version': '1.0',
            },
            follow=True,
        )

    alice = django_user_model.objects.get(username='alice')
    bob = django_user_model.objects.get(username='bob')

    # Шаг 2: Bob подписывается на Alice
    Subscribe.objects.create(subscribe_from=bob, subscribe_to=alice)

    # Шаг 3: Проверяем подписку в профиле Bob
    client.force_login(bob)
    response = client.get(reverse('profile'))
    assert response.context['number_of_subscribed_users'] == 1

    # Шаг 4: Bob настраивает публикацию статистики
    with patch('account.views.statistics.logger'):
        client.post(
            reverse('save_share_settings'),
            data={
                'switch_share_general': 'on',
                'switch_share_dashboard': 'on',
                'switch_share_city_map': 'on',
            },
        )

    # Шаг 5: Alice проверяет своих подписчиков и видит Bob с can_subscribe=True
    client.force_login(alice)
    response = client.get(reverse('profile'))

    assert response.context['number_of_subscriber_users'] == 1
    subscriber = response.context['subscriber_users'][0]
    assert subscriber.username == 'bob'
    assert subscriber.can_subscribe is True

    # Шаг 6: Удаляем подписку
    Subscribe.objects.filter(subscribe_from=bob, subscribe_to=alice).delete()

    # Шаг 7: Проверяем, что подписки больше нет
    response = client.get(reverse('profile'))
    assert response.context['number_of_subscriber_users'] == 0
