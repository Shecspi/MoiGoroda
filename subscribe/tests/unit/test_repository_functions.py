"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.contrib.auth.models import User

from subscribe.infrastructure.models import Subscribe
from subscribe.repository import (
    is_user_has_subscriptions,
    is_subscribed,
    get_all_subscriptions,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestRepositoryFunctions:
    """Тесты для функций в subscribe/repository.py"""

    def test_is_user_has_subscriptions_true(self) -> None:
        """Тест что функция возвращает True если у пользователя есть подписки"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')

        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

        assert is_user_has_subscriptions(user1.id) is True

    def test_is_user_has_subscriptions_false(self) -> None:
        """Тест что функция возвращает False если у пользователя нет подписок"""
        user1 = User.objects.create_user(username='user1', password='password1')

        assert is_user_has_subscriptions(user1.id) is False

    def test_is_user_has_subscriptions_does_not_count_subscriptions_to_user(self) -> None:
        """Тест что функция не учитывает подписки НА пользователя"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')

        # user2 подписывается на user1
        Subscribe.objects.create(subscribe_from=user2, subscribe_to=user1)

        # У user1 нет подписок (он не подписан ни на кого)
        assert is_user_has_subscriptions(user1.id) is False

    def test_is_subscribed_true(self) -> None:
        """Тест что функция возвращает True если подписка существует"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')

        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

        assert is_subscribed(user1.id, user2.id) is True

    def test_is_subscribed_false(self) -> None:
        """Тест что функция возвращает False если подписка не существует"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')

        assert is_subscribed(user1.id, user2.id) is False

    def test_is_subscribed_not_symmetric(self) -> None:
        """Тест что подписка не симметрична"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')

        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

        assert is_subscribed(user1.id, user2.id) is True
        assert is_subscribed(user2.id, user1.id) is False

    def test_get_all_subscriptions_returns_correct_data(self) -> None:
        """Тест что функция возвращает правильные данные о подписках"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')
        user3 = User.objects.create_user(username='user3', password='password3')

        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)
        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user3)

        subscriptions = get_all_subscriptions(user1.id)

        assert len(subscriptions) == 2
        assert {'to_id': user2.id, 'username': 'user2'} in subscriptions
        assert {'to_id': user3.id, 'username': 'user3'} in subscriptions

    def test_get_all_subscriptions_empty_list(self) -> None:
        """Тест что функция возвращает пустой список если нет подписок"""
        user1 = User.objects.create_user(username='user1', password='password1')

        subscriptions = get_all_subscriptions(user1.id)

        assert subscriptions == []

    def test_get_all_subscriptions_does_not_return_subscriptions_to_user(self) -> None:
        """Тест что функция не возвращает подписки НА пользователя"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')

        # user2 подписывается на user1
        Subscribe.objects.create(subscribe_from=user2, subscribe_to=user1)

        subscriptions = get_all_subscriptions(user1.id)

        assert subscriptions == []

    def test_get_all_subscriptions_ordered_correctly(self) -> None:
        """Тест что подписки возвращаются в правильном порядке"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')
        user3 = User.objects.create_user(username='user3', password='password3')
        user4 = User.objects.create_user(username='user4', password='password4')

        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)
        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user3)
        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user4)

        subscriptions = get_all_subscriptions(user1.id)

        # Проверяем что все подписки вернулись
        assert len(subscriptions) == 3

        # Проверяем что каждая подписка содержит правильные поля
        for subscription in subscriptions:
            assert 'to_id' in subscription
            assert 'username' in subscription
            assert isinstance(subscription['to_id'], int)
            assert isinstance(subscription['username'], str)
