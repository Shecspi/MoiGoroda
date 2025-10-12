"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from datetime import date, timedelta, datetime
from django.contrib.auth.models import User

from advertisement.models import AdvertisementException
from advertisement.templatetags.excluded_users import get_excluded_users


@pytest.mark.integration
@pytest.mark.django_db
def test_get_excluded_users_returns_empty_tuple_when_no_exceptions() -> None:
    """Тест что get_excluded_users возвращает пустой tuple при отсутствии исключений"""
    result = get_excluded_users()  # type: ignore[no-untyped-call]

    assert result == ()
    assert isinstance(result, tuple)


@pytest.mark.integration
@pytest.mark.django_db
def test_get_excluded_users_returns_active_exceptions_only(django_user_model: Any) -> None:
    """Тест что get_excluded_users возвращает только активные исключения"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    user3 = django_user_model.objects.create_user(username='user3', password='password123')

    # Создаём исключения: прошедшее, сегодняшнее, будущее
    past_date = date.today() - timedelta(days=1)
    today = date.today()
    future_date = date.today() + timedelta(days=10)

    AdvertisementException.objects.create(user=user1, deadline=past_date)
    AdvertisementException.objects.create(user=user2, deadline=today)
    AdvertisementException.objects.create(user=user3, deadline=future_date)

    result = get_excluded_users()  # type: ignore[no-untyped-call]

    # Должны вернуться только user2 и user3 (deadline >= сегодня)
    assert len(result) >= 2
    assert user2.id in result
    assert user3.id in result
    assert user1.id not in result


@pytest.mark.integration
@pytest.mark.django_db
def test_get_excluded_users_with_single_exception(django_user_model: Any) -> None:
    """Тест get_excluded_users с одним исключением"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    deadline = date.today() + timedelta(days=30)

    AdvertisementException.objects.create(user=user, deadline=deadline)

    result = get_excluded_users()  # type: ignore[no-untyped-call]

    assert len(result) == 1
    assert user.id in result


@pytest.mark.integration
@pytest.mark.django_db
def test_get_excluded_users_with_multiple_exceptions(django_user_model: Any) -> None:
    """Тест get_excluded_users с несколькими исключениями"""
    users = [
        django_user_model.objects.create_user(username=f'user{i}', password='password123')
        for i in range(5)
    ]

    deadline = date.today() + timedelta(days=30)
    for user in users:
        AdvertisementException.objects.create(user=user, deadline=deadline)

    result = get_excluded_users()  # type: ignore[no-untyped-call]

    assert len(result) == 5
    for user in users:
        assert user.id in result


@pytest.mark.integration
@pytest.mark.django_db
def test_get_excluded_users_returns_only_user_ids(django_user_model: Any) -> None:
    """Тест что get_excluded_users возвращает только ID пользователей"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    deadline = date.today() + timedelta(days=30)
    AdvertisementException.objects.create(user=user1, deadline=deadline)
    AdvertisementException.objects.create(user=user2, deadline=deadline)

    result = get_excluded_users()  # type: ignore[no-untyped-call]

    # Проверяем, что все элементы - это int (ID)
    assert all(isinstance(user_id, int) for user_id in result)
    assert user1.id in result
    assert user2.id in result


@pytest.mark.integration
@pytest.mark.django_db
def test_get_excluded_users_ignores_expired_exceptions(django_user_model: Any) -> None:
    """Тест что get_excluded_users игнорирует истёкшие исключения"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    # Создаём истёкшее и активное исключения
    expired_deadline = date.today() - timedelta(days=5)
    active_deadline = date.today() + timedelta(days=5)

    AdvertisementException.objects.create(user=user1, deadline=expired_deadline)
    AdvertisementException.objects.create(user=user2, deadline=active_deadline)

    result = get_excluded_users()  # type: ignore[no-untyped-call]

    assert user2.id in result
    assert user1.id not in result


@pytest.mark.integration
@pytest.mark.django_db
def test_get_excluded_users_includes_today_deadline(django_user_model: Any) -> None:
    """Тест что get_excluded_users включает исключения с deadline = сегодня"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Deadline = сегодня
    AdvertisementException.objects.create(user=user, deadline=date.today())

    result = get_excluded_users()  # type: ignore[no-untyped-call]

    # Исключение с deadline=сегодня должно включаться
    assert user.id in result


@pytest.mark.integration
@pytest.mark.django_db
def test_get_excluded_users_multiple_exceptions_for_same_user(django_user_model: Any) -> None:
    """Тест что для одного пользователя с несколькими исключениями ID возвращается несколько раз"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    deadline1 = date.today() + timedelta(days=10)
    deadline2 = date.today() + timedelta(days=20)

    AdvertisementException.objects.create(user=user, deadline=deadline1)
    AdvertisementException.objects.create(user=user, deadline=deadline2)

    result = get_excluded_users()  # type: ignore[no-untyped-call]

    # ID должен встречаться дважды
    assert result.count(user.id) == 2


@pytest.mark.integration
@pytest.mark.django_db
def test_get_excluded_users_with_deleted_user() -> None:
    """Тест что после удаления пользователя его исключение тоже удаляется"""
    user = User.objects.create_user(username='testuser', password='password123')
    deadline = date.today() + timedelta(days=30)

    AdvertisementException.objects.create(user=user, deadline=deadline)

    # Удаляем пользователя
    user_id = user.id
    user.delete()

    result = get_excluded_users()  # type: ignore[no-untyped-call]

    # ID удалённого пользователя не должен быть в результате
    assert user_id not in result


@pytest.mark.integration
@pytest.mark.django_db
def test_get_excluded_users_performance_with_many_records(django_user_model: Any) -> None:
    """Тест производительности get_excluded_users с большим количеством записей"""
    # Создаём 100 пользователей и исключений
    users = [
        django_user_model.objects.create_user(username=f'user{i}', password='password123')
        for i in range(100)
    ]

    deadline = date.today() + timedelta(days=30)
    for user in users:
        AdvertisementException.objects.create(user=user, deadline=deadline)

    result = get_excluded_users()  # type: ignore[no-untyped-call]

    assert len(result) == 100
    assert all(user.id in result for user in users)


# Импорт Mock в конце файла
from unittest.mock import Mock

