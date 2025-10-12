"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any

from account.models import ShareSettings
from account.dto import SubscriberUserDTO, SubscribedUserDTO
from account.repository import get_subscriber_users, get_subscribed_users
from subscribe.infrastructure.models import Subscribe


# ===== Фикстуры =====


@pytest.fixture
def create_users(django_user_model: Any) -> Any:
    """Создаёт тестовых пользователей"""
    user1 = django_user_model.objects.create_user(
        username='user1', email='user1@test.com', password='password123'
    )
    user2 = django_user_model.objects.create_user(
        username='user2', email='user2@test.com', password='password123'
    )
    user3 = django_user_model.objects.create_user(
        username='user3', email='user3@test.com', password='password123'
    )
    return {'user1': user1, 'user2': user2, 'user3': user3}


# ===== Тесты для get_subscribed_users =====


@pytest.mark.integration
@pytest.mark.django_db
def test_get_subscribed_users_empty_list(create_users: Any) -> None:
    """Тест get_subscribed_users без подписок"""
    users = create_users
    result = get_subscribed_users(user_id=users['user1'].id)

    assert result == []


@pytest.mark.integration
@pytest.mark.django_db
def test_get_subscribed_users_single_subscription(create_users: Any) -> None:
    """Тест get_subscribed_users с одной подпиской"""
    users = create_users

    # user1 подписывается на user2
    Subscribe.objects.create(subscribe_from=users['user1'], subscribe_to=users['user2'])

    result = get_subscribed_users(user_id=users['user1'].id)

    assert len(result) == 1
    assert isinstance(result[0], SubscribedUserDTO)
    assert result[0].id == users['user2'].id
    assert result[0].username == 'user2'


@pytest.mark.integration
@pytest.mark.django_db
def test_get_subscribed_users_multiple_subscriptions(create_users: Any) -> None:
    """Тест get_subscribed_users с несколькими подписками"""
    users = create_users

    # user1 подписывается на user2 и user3
    Subscribe.objects.create(subscribe_from=users['user1'], subscribe_to=users['user2'])
    Subscribe.objects.create(subscribe_from=users['user1'], subscribe_to=users['user3'])

    result = get_subscribed_users(user_id=users['user1'].id)

    assert len(result) == 2
    usernames = {dto.username for dto in result}
    assert usernames == {'user2', 'user3'}


@pytest.mark.integration
@pytest.mark.django_db
def test_get_subscribed_users_only_own_subscriptions(create_users: Any) -> None:
    """Тест что get_subscribed_users возвращает только подписки текущего пользователя"""
    users = create_users

    # user1 подписывается на user2
    Subscribe.objects.create(subscribe_from=users['user1'], subscribe_to=users['user2'])

    # user3 подписывается на user2
    Subscribe.objects.create(subscribe_from=users['user3'], subscribe_to=users['user2'])

    result = get_subscribed_users(user_id=users['user1'].id)

    # user1 должен видеть только свою подписку на user2
    assert len(result) == 1
    assert result[0].username == 'user2'


# ===== Тесты для get_subscriber_users =====


@pytest.mark.integration
@pytest.mark.django_db
def test_get_subscriber_users_empty_list(create_users: Any) -> None:
    """Тест get_subscriber_users без подписчиков"""
    users = create_users
    result = get_subscriber_users(user_id=users['user1'].id)

    assert result == []


@pytest.mark.integration
@pytest.mark.django_db
def test_get_subscriber_users_single_subscriber(create_users: Any) -> None:
    """Тест get_subscriber_users с одним подписчиком"""
    users = create_users

    # user2 подписывается на user1
    Subscribe.objects.create(subscribe_from=users['user2'], subscribe_to=users['user1'])

    result = get_subscriber_users(user_id=users['user1'].id)

    assert len(result) == 1
    assert isinstance(result[0], SubscriberUserDTO)
    assert result[0].id == users['user2'].id
    assert result[0].username == 'user2'
    assert result[0].can_subscribe is False  # По умолчанию False, если нет ShareSettings


@pytest.mark.integration
@pytest.mark.django_db
def test_get_subscriber_users_with_share_settings_true(create_users: Any) -> None:
    """Тест get_subscriber_users с настройками публикации (can_share=True)"""
    users = create_users

    # user2 подписывается на user1
    Subscribe.objects.create(subscribe_from=users['user2'], subscribe_to=users['user1'])

    # Создаём ShareSettings для user2 с can_share=True
    ShareSettings.objects.create(user=users['user2'], can_share=True)

    result = get_subscriber_users(user_id=users['user1'].id)

    assert len(result) == 1
    assert result[0].can_subscribe is True


@pytest.mark.integration
@pytest.mark.django_db
def test_get_subscriber_users_with_share_settings_false(create_users: Any) -> None:
    """Тест get_subscriber_users с настройками публикации (can_share=False)"""
    users = create_users

    # user2 подписывается на user1
    Subscribe.objects.create(subscribe_from=users['user2'], subscribe_to=users['user1'])

    # Создаём ShareSettings для user2 с can_share=False
    ShareSettings.objects.create(user=users['user2'], can_share=False)

    result = get_subscriber_users(user_id=users['user1'].id)

    assert len(result) == 1
    assert result[0].can_subscribe is False


@pytest.mark.integration
@pytest.mark.django_db
def test_get_subscriber_users_multiple_subscribers(create_users: Any) -> None:
    """Тест get_subscriber_users с несколькими подписчиками"""
    users = create_users

    # user2 и user3 подписываются на user1
    Subscribe.objects.create(subscribe_from=users['user2'], subscribe_to=users['user1'])
    Subscribe.objects.create(subscribe_from=users['user3'], subscribe_to=users['user1'])

    # Создаём ShareSettings для user2 с can_share=True
    ShareSettings.objects.create(user=users['user2'], can_share=True)

    result = get_subscriber_users(user_id=users['user1'].id)

    assert len(result) == 2

    # Проверяем can_subscribe для каждого подписчика
    user2_dto = next(dto for dto in result if dto.username == 'user2')
    user3_dto = next(dto for dto in result if dto.username == 'user3')

    assert user2_dto.can_subscribe is True
    assert user3_dto.can_subscribe is False


@pytest.mark.integration
@pytest.mark.django_db
def test_get_subscriber_users_only_own_subscribers(create_users: Any) -> None:
    """Тест что get_subscriber_users возвращает только подписчиков текущего пользователя"""
    users = create_users

    # user2 подписывается на user1
    Subscribe.objects.create(subscribe_from=users['user2'], subscribe_to=users['user1'])

    # user2 подписывается на user3
    Subscribe.objects.create(subscribe_from=users['user2'], subscribe_to=users['user3'])

    result = get_subscriber_users(user_id=users['user1'].id)

    # user1 должен видеть только user2 как подписчика
    assert len(result) == 1
    assert result[0].username == 'user2'


@pytest.mark.integration
@pytest.mark.django_db
def test_get_subscriber_users_with_deleted_share_settings(create_users: Any) -> None:
    """Тест get_subscriber_users после удаления ShareSettings"""
    users = create_users

    # user2 подписывается на user1
    Subscribe.objects.create(subscribe_from=users['user2'], subscribe_to=users['user1'])

    # Создаём и удаляем ShareSettings
    share_settings = ShareSettings.objects.create(user=users['user2'], can_share=True)
    share_settings.delete()

    result = get_subscriber_users(user_id=users['user1'].id)

    assert len(result) == 1
    assert result[0].can_subscribe is False


# ===== Комплексные тесты =====


@pytest.mark.integration
@pytest.mark.django_db
def test_subscriptions_are_bidirectional_independent(create_users: Any) -> None:
    """Тест что подписки независимы в обоих направлениях"""
    users = create_users

    # user1 подписывается на user2
    Subscribe.objects.create(subscribe_from=users['user1'], subscribe_to=users['user2'])

    # Проверяем, что user1 подписан на user2
    subscribed = get_subscribed_users(user_id=users['user1'].id)
    assert len(subscribed) == 1
    assert subscribed[0].username == 'user2'

    # Проверяем, что user2 НЕ подписан на user1
    subscribed_user2 = get_subscribed_users(user_id=users['user2'].id)
    assert len(subscribed_user2) == 0

    # Проверяем подписчиков user2
    subscribers = get_subscriber_users(user_id=users['user2'].id)
    assert len(subscribers) == 1
    assert subscribers[0].username == 'user1'


@pytest.mark.integration
@pytest.mark.django_db
def test_mutual_subscriptions(create_users: Any) -> None:
    """Тест взаимных подписок"""
    users = create_users

    # user1 подписывается на user2
    Subscribe.objects.create(subscribe_from=users['user1'], subscribe_to=users['user2'])

    # user2 подписывается на user1
    Subscribe.objects.create(subscribe_from=users['user2'], subscribe_to=users['user1'])

    # Проверяем подписки user1
    subscribed_user1 = get_subscribed_users(user_id=users['user1'].id)
    assert len(subscribed_user1) == 1
    assert subscribed_user1[0].username == 'user2'

    # Проверяем подписки user2
    subscribed_user2 = get_subscribed_users(user_id=users['user2'].id)
    assert len(subscribed_user2) == 1
    assert subscribed_user2[0].username == 'user1'

    # Проверяем подписчиков user1
    subscribers_user1 = get_subscriber_users(user_id=users['user1'].id)
    assert len(subscribers_user1) == 1
    assert subscribers_user1[0].username == 'user2'

    # Проверяем подписчиков user2
    subscribers_user2 = get_subscriber_users(user_id=users['user2'].id)
    assert len(subscribers_user2) == 1
    assert subscribers_user2[0].username == 'user1'


@pytest.mark.integration
@pytest.mark.django_db
def test_repository_functions_with_nonexistent_user() -> None:
    """Тест функций репозитория с несуществующим пользователем"""
    # Проверяем, что функции не падают с несуществующим ID
    result_subscribed = get_subscribed_users(user_id=99999)
    result_subscribers = get_subscriber_users(user_id=99999)

    assert result_subscribed == []
    assert result_subscribers == []


@pytest.mark.integration
@pytest.mark.django_db
def test_share_settings_update_reflects_in_subscribers(create_users: Any) -> None:
    """Тест что обновление ShareSettings отражается в get_subscriber_users"""
    users = create_users

    # user2 подписывается на user1
    Subscribe.objects.create(subscribe_from=users['user2'], subscribe_to=users['user1'])

    # Создаём ShareSettings с can_share=False
    share_settings = ShareSettings.objects.create(user=users['user2'], can_share=False)

    result = get_subscriber_users(user_id=users['user1'].id)
    assert result[0].can_subscribe is False

    # Обновляем ShareSettings на can_share=True
    share_settings.can_share = True
    share_settings.save()

    result = get_subscriber_users(user_id=users['user1'].id)
    assert result[0].can_subscribe is True
