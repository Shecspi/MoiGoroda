"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from subscribe.domain.entities import (
    Action,
    SubscriptionRequest,
    DeleteSubscriberRequest,
    Notification,
)


@pytest.mark.unit
class TestActionEnum:
    """Тесты для enum Action"""

    def test_action_enum_values(self) -> None:
        """Тест значений enum Action"""
        assert Action.subscribe == 'subscribe'
        assert Action.unsubscribe == 'unsubscribe'

    def test_action_enum_members(self) -> None:
        """Тест что enum имеет правильные члены"""
        assert set(Action) == {Action.subscribe, Action.unsubscribe}

    def test_action_enum_count(self) -> None:
        """Тест количества членов enum"""
        assert len(Action) == 2

    def test_action_enum_string_representation(self) -> None:
        """Тест строкового представления"""
        assert str(Action.subscribe) == 'subscribe'
        assert str(Action.unsubscribe) == 'unsubscribe'


@pytest.mark.unit
class TestSubscriptionRequest:
    """Тесты для SubscriptionRequest"""

    def test_subscription_request_valid_data(self) -> None:
        """Тест создания запроса с валидными данными"""
        request = SubscriptionRequest(from_id=1, to_id=2, action=Action.subscribe)

        assert request.from_id == 1
        assert request.to_id == 2
        assert request.action == Action.subscribe

    def test_subscription_request_from_json(self) -> None:
        """Тест создания запроса из JSON"""
        json_data = '{"from_id": 1, "to_id": 2, "action": "subscribe"}'
        request = SubscriptionRequest.model_validate_json(json_data)

        assert request.from_id == 1
        assert request.to_id == 2
        assert request.action == Action.subscribe

    def test_subscription_request_invalid_action(self) -> None:
        """Тест что невалидный action вызывает ошибку"""
        json_data = '{"from_id": 1, "to_id": 2, "action": "invalid"}'

        with pytest.raises(ValidationError) as exc_info:
            SubscriptionRequest.model_validate_json(json_data)

        # Проверяем что ошибка связана с полем action
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('action',) for error in errors)

    def test_subscription_request_missing_field(self) -> None:
        """Тест что отсутствие обязательного поля вызывает ошибку"""
        json_data = '{"from_id": 1, "to_id": 2}'

        with pytest.raises(ValidationError) as exc_info:
            SubscriptionRequest.model_validate_json(json_data)

        # Проверяем что ошибка связана с полем action
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('action',) for error in errors)

    def test_subscription_request_invalid_type(self) -> None:
        """Тест что невалидный тип данных вызывает ошибку"""
        json_data = '{"from_id": "not_an_int", "to_id": 2, "action": "subscribe"}'

        with pytest.raises(ValidationError) as exc_info:
            SubscriptionRequest.model_validate_json(json_data)

        errors = exc_info.value.errors()
        assert any(error['loc'] == ('from_id',) for error in errors)

    def test_subscription_request_unsubscribe_action(self) -> None:
        """Тест создания запроса с действием unsubscribe"""
        request = SubscriptionRequest(from_id=1, to_id=2, action=Action.unsubscribe)

        assert request.action == Action.unsubscribe


@pytest.mark.unit
class TestDeleteSubscriberRequest:
    """Тесты для DeleteSubscriberRequest"""

    def test_delete_subscriber_request_valid_data(self) -> None:
        """Тест создания запроса с валидными данными"""
        request = DeleteSubscriberRequest(user_id=1)

        assert request.user_id == 1

    def test_delete_subscriber_request_from_json(self) -> None:
        """Тест создания запроса из JSON"""
        json_data = '{"user_id": 1}'
        request = DeleteSubscriberRequest.model_validate_json(json_data)

        assert request.user_id == 1

    def test_delete_subscriber_request_missing_field(self) -> None:
        """Тест что отсутствие обязательного поля вызывает ошибку"""
        json_data = '{}'

        with pytest.raises(ValidationError) as exc_info:
            DeleteSubscriberRequest.model_validate_json(json_data)

        errors = exc_info.value.errors()
        assert any(error['loc'] == ('user_id',) for error in errors)

    def test_delete_subscriber_request_invalid_type(self) -> None:
        """Тест что невалидный тип данных вызывает ошибку"""
        json_data = '{"user_id": "not_an_int"}'

        with pytest.raises(ValidationError) as exc_info:
            DeleteSubscriberRequest.model_validate_json(json_data)

        errors = exc_info.value.errors()
        assert any(error['loc'] == ('user_id',) for error in errors)


@pytest.mark.unit
class TestNotification:
    """Тесты для Notification dataclass"""

    def test_notification_creation_with_all_fields(self) -> None:
        """Тест создания уведомления со всеми полями"""
        read_at = datetime.now()
        notification = Notification(
            id=1,
            city_id=10,
            city_title='Москва',
            region_id=20,
            region_title='Московская область',
            country_code='RU',
            country_title='Россия',
            is_read=True,
            sender_id=5,
            sender_username='testuser',
            read_at=read_at,
        )

        assert notification.id == 1
        assert notification.city_id == 10
        assert notification.city_title == 'Москва'
        assert notification.region_id == 20
        assert notification.region_title == 'Московская область'
        assert notification.country_code == 'RU'
        assert notification.country_title == 'Россия'
        assert notification.is_read is True
        assert notification.sender_id == 5
        assert notification.sender_username == 'testuser'
        assert notification.read_at == read_at

    def test_notification_creation_without_read_at(self) -> None:
        """Тест создания уведомления без поля read_at (должно быть None по умолчанию)"""
        notification = Notification(
            id=1,
            city_id=10,
            city_title='Москва',
            region_id=20,
            region_title='Московская область',
            country_code='RU',
            country_title='Россия',
            is_read=False,
            sender_id=5,
            sender_username='testuser',
        )

        assert notification.read_at is None

    def test_notification_is_dataclass(self) -> None:
        """Тест что Notification является dataclass"""
        from dataclasses import is_dataclass

        assert is_dataclass(Notification)

    def test_notification_fields_immutability(self) -> None:
        """Тест что поля уведомления можно изменять (dataclass не frozen)"""
        notification = Notification(
            id=1,
            city_id=10,
            city_title='Москва',
            region_id=20,
            region_title='Московская область',
            country_code='RU',
            country_title='Россия',
            is_read=False,
            sender_id=5,
            sender_username='testuser',
        )

        # Изменяем статус прочитанности
        notification.is_read = True
        notification.read_at = datetime.now()

        assert notification.is_read is True
        assert notification.read_at is not None
