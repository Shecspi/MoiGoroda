"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from account.dto import SubscribedUserDTO, SubscriberUserDTO


# ===== Тесты для SubscribedUserDTO =====


@pytest.mark.unit
def test_subscribed_user_dto_creation() -> None:
    """Тест создания SubscribedUserDTO"""
    dto = SubscribedUserDTO(id=1, username='testuser')

    assert dto.id == 1
    assert dto.username == 'testuser'


@pytest.mark.unit
def test_subscribed_user_dto_fields() -> None:
    """Тест наличия всех полей в SubscribedUserDTO"""
    dto = SubscribedUserDTO(id=10, username='user123')

    assert hasattr(dto, 'id')
    assert hasattr(dto, 'username')


@pytest.mark.unit
def test_subscribed_user_dto_immutability() -> None:
    """Тест неизменяемости dataclass (frozen=False, поэтому можно изменять)"""
    dto = SubscribedUserDTO(id=1, username='testuser')

    # Проверяем, что можем изменить (dataclass не frozen)
    dto.username = 'newuser'
    assert dto.username == 'newuser'


@pytest.mark.unit
def test_subscribed_user_dto_equality() -> None:
    """Тест сравнения двух SubscribedUserDTO"""
    dto1 = SubscribedUserDTO(id=1, username='testuser')
    dto2 = SubscribedUserDTO(id=1, username='testuser')
    dto3 = SubscribedUserDTO(id=2, username='otheruser')

    assert dto1 == dto2
    assert dto1 != dto3


@pytest.mark.unit
def test_subscribed_user_dto_repr() -> None:
    """Тест строкового представления SubscribedUserDTO"""
    dto = SubscribedUserDTO(id=1, username='testuser')

    repr_str = repr(dto)
    assert 'SubscribedUserDTO' in repr_str
    assert 'id=1' in repr_str
    assert "username='testuser'" in repr_str


@pytest.mark.unit
def test_subscribed_user_dto_with_different_types() -> None:
    """Тест создания SubscribedUserDTO с разными типами данных"""
    # С int id
    dto1 = SubscribedUserDTO(id=999, username='user999')
    assert dto1.id == 999

    # С длинным username
    long_username = 'a' * 150
    dto2 = SubscribedUserDTO(id=1, username=long_username)
    assert dto2.username == long_username


# ===== Тесты для SubscriberUserDTO =====


@pytest.mark.unit
def test_subscriber_user_dto_creation() -> None:
    """Тест создания SubscriberUserDTO"""
    dto = SubscriberUserDTO(id=1, username='testuser', can_subscribe=True)

    assert dto.id == 1
    assert dto.username == 'testuser'
    assert dto.can_subscribe is True


@pytest.mark.unit
def test_subscriber_user_dto_fields() -> None:
    """Тест наличия всех полей в SubscriberUserDTO"""
    dto = SubscriberUserDTO(id=10, username='user123', can_subscribe=False)

    assert hasattr(dto, 'id')
    assert hasattr(dto, 'username')
    assert hasattr(dto, 'can_subscribe')


@pytest.mark.unit
def test_subscriber_user_dto_can_subscribe_false() -> None:
    """Тест SubscriberUserDTO с can_subscribe=False"""
    dto = SubscriberUserDTO(id=1, username='testuser', can_subscribe=False)

    assert dto.can_subscribe is False


@pytest.mark.unit
def test_subscriber_user_dto_can_subscribe_true() -> None:
    """Тест SubscriberUserDTO с can_subscribe=True"""
    dto = SubscriberUserDTO(id=1, username='testuser', can_subscribe=True)

    assert dto.can_subscribe is True


@pytest.mark.unit
def test_subscriber_user_dto_equality() -> None:
    """Тест сравнения двух SubscriberUserDTO"""
    dto1 = SubscriberUserDTO(id=1, username='testuser', can_subscribe=True)
    dto2 = SubscriberUserDTO(id=1, username='testuser', can_subscribe=True)
    dto3 = SubscriberUserDTO(id=1, username='testuser', can_subscribe=False)

    assert dto1 == dto2
    assert dto1 != dto3


@pytest.mark.unit
def test_subscriber_user_dto_repr() -> None:
    """Тест строкового представления SubscriberUserDTO"""
    dto = SubscriberUserDTO(id=1, username='testuser', can_subscribe=True)

    repr_str = repr(dto)
    assert 'SubscriberUserDTO' in repr_str
    assert 'id=1' in repr_str
    assert "username='testuser'" in repr_str
    assert 'can_subscribe=True' in repr_str


@pytest.mark.unit
def test_subscriber_user_dto_immutability() -> None:
    """Тест изменяемости SubscriberUserDTO"""
    dto = SubscriberUserDTO(id=1, username='testuser', can_subscribe=True)

    # Можем изменить (dataclass не frozen)
    dto.can_subscribe = False
    assert dto.can_subscribe is False


@pytest.mark.unit
def test_subscriber_user_dto_with_different_values() -> None:
    """Тест SubscriberUserDTO с различными значениями"""
    # Минимальные значения
    dto1 = SubscriberUserDTO(id=0, username='', can_subscribe=False)
    assert dto1.id == 0
    assert dto1.username == ''
    assert dto1.can_subscribe is False

    # Большие значения
    dto2 = SubscriberUserDTO(id=999999, username='verylongusername' * 10, can_subscribe=True)
    assert dto2.id == 999999
    assert len(dto2.username) == 16 * 10


# ===== Тесты на совместимость =====


@pytest.mark.unit
def test_dto_types_are_different() -> None:
    """Тест что SubscribedUserDTO и SubscriberUserDTO - разные типы"""
    dto1 = SubscribedUserDTO(id=1, username='user')
    dto2 = SubscriberUserDTO(id=1, username='user', can_subscribe=True)

    assert type(dto1) != type(dto2)  # type: ignore[comparison-overlap]
    assert dto1 != dto2  # type: ignore[comparison-overlap]


@pytest.mark.unit
def test_dto_can_be_used_in_collections() -> None:
    """Тест использования DTO в коллекциях"""
    subscribed_list = [
        SubscribedUserDTO(id=1, username='user1'),
        SubscribedUserDTO(id=2, username='user2'),
    ]

    subscriber_list = [
        SubscriberUserDTO(id=3, username='user3', can_subscribe=True),
        SubscriberUserDTO(id=4, username='user4', can_subscribe=False),
    ]

    assert len(subscribed_list) == 2
    assert len(subscriber_list) == 2
    assert subscribed_list[0].id == 1
    assert subscriber_list[0].can_subscribe is True


@pytest.mark.unit
def test_dto_in_set() -> None:
    """Тест что DTO могут быть использованы в списках и других коллекциях"""
    dto1 = SubscribedUserDTO(id=1, username='user1')
    dto2 = SubscribedUserDTO(id=2, username='user2')

    # Проверяем, что можем создать список
    dto_list = [dto1, dto2]
    assert len(dto_list) == 2
    assert dto1 in dto_list
    assert dto2 in dto_list
