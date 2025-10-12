"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from datetime import date, timedelta

from advertisement.models import AdvertisementException
from advertisement.templatetags.excluded_users import get_excluded_users


# ===== E2E тесты для сценариев исключения рекламы =====


@pytest.mark.e2e
@pytest.mark.django_db
def test_create_exception_and_check_exclusion_flow(django_user_model: Any) -> None:
    """
    E2E тест: Создание пользователя -> Создание исключения -> Проверка в списке исключённых
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Шаг 2: Проверяем, что пользователь не в списке исключённых
    excluded_users = get_excluded_users()
    assert user.id not in excluded_users

    # Шаг 3: Создаём исключение для пользователя
    deadline = date.today() + timedelta(days=30)
    exception = AdvertisementException.objects.create(user=user, deadline=deadline)

    # Шаг 4: Проверяем, что пользователь теперь в списке исключённых
    excluded_users = get_excluded_users()
    assert user.id in excluded_users

    # Шаг 5: Удаляем исключение
    exception.delete()

    # Шаг 6: Проверяем, что пользователь больше не в списке
    excluded_users = get_excluded_users()
    assert user.id not in excluded_users


@pytest.mark.e2e
@pytest.mark.django_db
def test_exception_expiration_flow(django_user_model: Any) -> None:
    """
    E2E тест: Создание исключения -> Истечение срока -> Проверка отсутствия в списке
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Шаг 2: Создаём исключение с будущей датой
    future_deadline = date.today() + timedelta(days=10)
    exception = AdvertisementException.objects.create(user=user, deadline=future_deadline)

    # Шаг 3: Проверяем, что пользователь в списке
    excluded_users = get_excluded_users()
    assert user.id in excluded_users

    # Шаг 4: Изменяем deadline на прошедшую дату (имитация истечения срока)
    past_deadline = date.today() - timedelta(days=1)
    exception.deadline = past_deadline
    exception.save()

    # Шаг 5: Проверяем, что пользователь больше не в списке
    excluded_users = get_excluded_users()
    assert user.id not in excluded_users


@pytest.mark.e2e
@pytest.mark.django_db
def test_multiple_users_exception_management_flow(django_user_model: Any) -> None:
    """
    E2E тест: Управление исключениями для нескольких пользователей
    """
    # Шаг 1: Создаём трёх пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    user3 = django_user_model.objects.create_user(username='user3', password='password123')

    # Шаг 2: Проверяем, что никто не исключён
    excluded_users = get_excluded_users()
    assert len(excluded_users) == 0

    # Шаг 3: Добавляем исключения для user1 и user2
    deadline = date.today() + timedelta(days=30)
    AdvertisementException.objects.create(user=user1, deadline=deadline)
    AdvertisementException.objects.create(user=user2, deadline=deadline)

    # Шаг 4: Проверяем список исключённых
    excluded_users = get_excluded_users()
    assert len(excluded_users) == 2
    assert user1.id in excluded_users
    assert user2.id in excluded_users
    assert user3.id not in excluded_users

    # Шаг 5: Добавляем исключение для user3
    AdvertisementException.objects.create(user=user3, deadline=deadline)

    # Шаг 6: Проверяем, что все три пользователя исключены
    excluded_users = get_excluded_users()
    assert len(excluded_users) == 3
    assert user1.id in excluded_users
    assert user2.id in excluded_users
    assert user3.id in excluded_users


@pytest.mark.e2e
@pytest.mark.django_db
def test_user_deletion_removes_exception_flow(django_user_model: Any) -> None:
    """
    E2E тест: Создание исключения -> Удаление пользователя -> Проверка cascade delete
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    user_id = user.id

    # Шаг 2: Создаём исключение
    deadline = date.today() + timedelta(days=30)
    AdvertisementException.objects.create(user=user, deadline=deadline)

    # Шаг 3: Проверяем, что исключение существует
    assert AdvertisementException.objects.filter(user_id=user_id).exists()
    excluded_users = get_excluded_users()
    assert user_id in excluded_users

    # Шаг 4: Удаляем пользователя
    user.delete()

    # Шаг 5: Проверяем, что исключение тоже удалилось
    assert not AdvertisementException.objects.filter(user_id=user_id).exists()
    excluded_users = get_excluded_users()
    assert user_id not in excluded_users


@pytest.mark.e2e
@pytest.mark.django_db
def test_update_exception_deadline_flow(django_user_model: Any) -> None:
    """
    E2E тест: Создание исключения -> Обновление deadline -> Проверка изменений
    """
    # Шаг 1: Создаём пользователя и исключение
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    initial_deadline = date.today() + timedelta(days=10)
    exception = AdvertisementException.objects.create(user=user, deadline=initial_deadline)

    # Шаг 2: Проверяем, что пользователь в списке
    excluded_users = get_excluded_users()
    assert user.id in excluded_users

    # Шаг 3: Обновляем deadline на прошедшую дату
    exception.deadline = date.today() - timedelta(days=1)
    exception.save()

    # Шаг 4: Проверяем, что пользователь больше не в списке
    excluded_users = get_excluded_users()
    assert user.id not in excluded_users

    # Шаг 5: Обновляем deadline на будущую дату
    exception.deadline = date.today() + timedelta(days=20)
    exception.save()

    # Шаг 6: Проверяем, что пользователь снова в списке
    excluded_users = get_excluded_users()
    assert user.id in excluded_users


@pytest.mark.e2e
@pytest.mark.django_db
def test_multiple_exceptions_for_single_user_flow(django_user_model: Any) -> None:
    """
    E2E тест: Один пользователь с несколькими исключениями
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Шаг 2: Создаём несколько исключений для одного пользователя
    deadline1 = date.today() + timedelta(days=10)
    deadline2 = date.today() + timedelta(days=20)
    deadline3 = date.today() + timedelta(days=30)

    AdvertisementException.objects.create(user=user, deadline=deadline1)
    AdvertisementException.objects.create(user=user, deadline=deadline2)
    AdvertisementException.objects.create(user=user, deadline=deadline3)

    # Шаг 3: Проверяем количество исключений
    exceptions_count = AdvertisementException.objects.filter(user=user).count()
    assert exceptions_count == 3

    # Шаг 4: Проверяем, что в списке исключённых ID встречается трижды
    excluded_users = get_excluded_users()
    assert excluded_users.count(user.id) == 3


@pytest.mark.e2e
@pytest.mark.django_db
def test_mixed_active_and_expired_exceptions_flow(django_user_model: Any) -> None:
    """
    E2E тест: Смешанные активные и истёкшие исключения
    """
    # Шаг 1: Создаём пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    user3 = django_user_model.objects.create_user(username='user3', password='password123')

    # Шаг 2: Создаём исключения с разными deadline
    past_deadline = date.today() - timedelta(days=5)
    today_deadline = date.today()
    future_deadline = date.today() + timedelta(days=15)

    AdvertisementException.objects.create(user=user1, deadline=past_deadline)
    AdvertisementException.objects.create(user=user2, deadline=today_deadline)
    AdvertisementException.objects.create(user=user3, deadline=future_deadline)

    # Шаг 3: Проверяем список исключённых
    excluded_users = get_excluded_users()

    # Должны быть только user2 и user3 (deadline >= сегодня)
    assert user1.id not in excluded_users
    assert user2.id in excluded_users
    assert user3.id in excluded_users

    # Шаг 4: Проверяем общее количество
    assert AdvertisementException.objects.count() == 3
    assert len(excluded_users) >= 2
