"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

import pytest

from subscribe.application.services import SubscriptionService
from subscribe.domain.entities import SubscriptionRequest, DeleteSubscriberRequest, Action


@pytest.fixture
def mock_user_repo(mocker: Any) -> Any:
    """Мокаем репозиторий пользователей"""
    return mocker.Mock()


@pytest.fixture
def mock_share_settings_repo(mocker: Any) -> Any:
    """Мокаем репозиторий настроек доступа"""
    return mocker.Mock()


@pytest.fixture
def mock_subscribe_repo(mocker: Any) -> Any:
    """Мокаем репозиторий подписок"""
    return mocker.Mock()


@pytest.fixture
def service(
    mock_user_repo: Any, mock_share_settings_repo: Any, mock_subscribe_repo: Any
) -> SubscriptionService:
    """Сервис с замоканными репозиториями"""
    return SubscriptionService(
        user_repo=mock_user_repo,
        share_settings_repo=mock_share_settings_repo,
        subscribe_repo=mock_subscribe_repo,
    )


@pytest.mark.unit
class TestSubscriptionServiceSave:
    """Тесты для метода save"""

    def test_save_subscribe_success(
        self,
        service: SubscriptionService,
        mock_user_repo: Any,
        mock_share_settings_repo: Any,
        mock_subscribe_repo: Any,
    ) -> None:
        """Тест успешной подписки"""
        request = SubscriptionRequest(from_id=1, to_id=2, action=Action.subscribe)
        mock_user_repo.exists.return_value = True
        mock_share_settings_repo.can_subscribe.return_value = True
        mock_subscribe_repo.is_subscribed.return_value = False

        result = service.save(request, current_user_id=1, is_superuser=False)

        assert result == {'status': 'subscribed'}
        mock_subscribe_repo.add.assert_called_once_with(1, 2)

    def test_save_subscribe_when_already_subscribed(
        self,
        service: SubscriptionService,
        mock_user_repo: Any,
        mock_share_settings_repo: Any,
        mock_subscribe_repo: Any,
    ) -> None:
        """Тест подписки когда уже подписан (идемпотентность)"""
        request = SubscriptionRequest(from_id=1, to_id=2, action=Action.subscribe)
        mock_user_repo.exists.return_value = True
        mock_share_settings_repo.can_subscribe.return_value = True
        mock_subscribe_repo.is_subscribed.return_value = True

        result = service.save(request, current_user_id=1, is_superuser=False)

        assert result == {'status': 'subscribed'}
        mock_subscribe_repo.add.assert_not_called()

    def test_save_unsubscribe_success(
        self,
        service: SubscriptionService,
        mock_user_repo: Any,
        mock_share_settings_repo: Any,
        mock_subscribe_repo: Any,
    ) -> None:
        """Тест успешной отписки"""
        request = SubscriptionRequest(from_id=1, to_id=2, action=Action.unsubscribe)
        mock_user_repo.exists.return_value = True
        mock_share_settings_repo.can_subscribe.return_value = True
        mock_subscribe_repo.is_subscribed.return_value = True

        result = service.save(request, current_user_id=1, is_superuser=False)

        assert result == {'status': 'unsubscribed'}
        mock_subscribe_repo.delete.assert_called_once_with(1, 2)

    def test_save_unsubscribe_when_not_subscribed(
        self,
        service: SubscriptionService,
        mock_user_repo: Any,
        mock_share_settings_repo: Any,
        mock_subscribe_repo: Any,
    ) -> None:
        """Тест отписки когда не подписан (идемпотентность)"""
        request = SubscriptionRequest(from_id=1, to_id=2, action=Action.unsubscribe)
        mock_user_repo.exists.return_value = True
        mock_share_settings_repo.can_subscribe.return_value = True
        mock_subscribe_repo.is_subscribed.return_value = False

        result = service.save(request, current_user_id=1, is_superuser=False)

        assert result == {'status': 'unsubscribed'}
        mock_subscribe_repo.delete.assert_not_called()

    def test_save_raises_permission_error_when_subscribing_for_another_user(
        self, service: SubscriptionService
    ) -> None:
        """Тест что нельзя подписываться за другого пользователя"""
        request = SubscriptionRequest(from_id=2, to_id=3, action=Action.subscribe)

        with pytest.raises(
            PermissionError, match='Нельзя оформлять подписки за других пользователей'
        ):
            service.save(request, current_user_id=1, is_superuser=False)

    def test_save_raises_value_error_when_from_user_not_exists(
        self, service: SubscriptionService, mock_user_repo: Any
    ) -> None:
        """Тест что ошибка если пользователь from_id не существует"""
        request = SubscriptionRequest(from_id=1, to_id=2, action=Action.subscribe)
        mock_user_repo.exists.side_effect = [False, True]

        with pytest.raises(ValueError, match='Передан неверный ID пользователя'):
            service.save(request, current_user_id=1, is_superuser=False)

    def test_save_raises_value_error_when_to_user_not_exists(
        self, service: SubscriptionService, mock_user_repo: Any
    ) -> None:
        """Тест что ошибка если пользователь to_id не существует"""
        request = SubscriptionRequest(from_id=1, to_id=2, action=Action.subscribe)
        mock_user_repo.exists.side_effect = [True, False]

        with pytest.raises(ValueError, match='Передан неверный ID пользователя'):
            service.save(request, current_user_id=1, is_superuser=False)

    def test_save_raises_permission_error_when_subscription_not_allowed(
        self,
        service: SubscriptionService,
        mock_user_repo: Any,
        mock_share_settings_repo: Any,
    ) -> None:
        """Тест что ошибка если пользователь не разрешил подписываться"""
        request = SubscriptionRequest(from_id=1, to_id=2, action=Action.subscribe)
        mock_user_repo.exists.return_value = True
        mock_share_settings_repo.can_subscribe.return_value = False

        with pytest.raises(PermissionError, match='Пользователь не разрешил подписываться на него'):
            service.save(request, current_user_id=1, is_superuser=False)

    def test_save_allows_superuser_to_subscribe_when_not_allowed(
        self,
        service: SubscriptionService,
        mock_user_repo: Any,
        mock_share_settings_repo: Any,
        mock_subscribe_repo: Any,
    ) -> None:
        """Тест что суперпользователь может подписаться даже если запрещено"""
        request = SubscriptionRequest(from_id=1, to_id=2, action=Action.subscribe)
        mock_user_repo.exists.return_value = True
        mock_share_settings_repo.can_subscribe.return_value = False
        mock_subscribe_repo.is_subscribed.return_value = False

        result = service.save(request, current_user_id=1, is_superuser=True)

        assert result == {'status': 'subscribed'}
        mock_subscribe_repo.add.assert_called_once_with(1, 2)


@pytest.mark.unit
class TestSubscriptionServiceDeleteSubscriber:
    """Тесты для метода delete_subscriber"""

    def test_delete_subscriber_success(
        self,
        service: SubscriptionService,
        mock_user_repo: Any,
        mock_subscribe_repo: Any,
    ) -> None:
        """Тест успешного удаления подписчика"""
        request = DeleteSubscriberRequest(user_id=1)
        mock_user_repo.exists.return_value = True
        mock_subscribe_repo.check.return_value = True

        result = service.delete_subscriber(request, current_user_id=2)

        assert result == {'status': 'success'}
        mock_subscribe_repo.delete.assert_called_once_with(1, 2)

    def test_delete_subscriber_raises_value_error_when_user_not_exists(
        self, service: SubscriptionService, mock_user_repo: Any
    ) -> None:
        """Тест что ошибка если пользователь не существует"""
        request = DeleteSubscriberRequest(user_id=999)
        mock_user_repo.exists.return_value = False

        with pytest.raises(ValueError, match='Передан неверный ID пользователя'):
            service.delete_subscriber(request, current_user_id=2)

    def test_delete_subscriber_raises_permission_error_when_not_subscribed(
        self,
        service: SubscriptionService,
        mock_user_repo: Any,
        mock_subscribe_repo: Any,
    ) -> None:
        """Тест что ошибка если пользователь не подписан"""
        request = DeleteSubscriberRequest(user_id=1)
        mock_user_repo.exists.return_value = True
        mock_subscribe_repo.check.return_value = False

        with pytest.raises(PermissionError, match='Пользователь не подписан'):
            service.delete_subscriber(request, current_user_id=2)

    def test_delete_subscriber_checks_subscription_in_correct_direction(
        self,
        service: SubscriptionService,
        mock_user_repo: Any,
        mock_subscribe_repo: Any,
    ) -> None:
        """Тест что проверка подписки идёт в правильном направлении"""
        request = DeleteSubscriberRequest(user_id=1)
        mock_user_repo.exists.return_value = True
        mock_subscribe_repo.check.return_value = True

        service.delete_subscriber(request, current_user_id=2)

        # Проверяем что user_id подписан на current_user_id
        mock_subscribe_repo.check.assert_called_once_with(1, 2)
        mock_subscribe_repo.delete.assert_called_once_with(1, 2)
