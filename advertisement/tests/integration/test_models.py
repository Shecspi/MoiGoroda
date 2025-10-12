"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from datetime import date, timedelta
from django.contrib.auth.models import User

from advertisement.models import AdvertisementException


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_create(django_user_model: Any) -> None:
    """Тест создания AdvertisementException"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    deadline = date.today() + timedelta(days=30)

    exception = AdvertisementException.objects.create(user=user, deadline=deadline)

    assert exception.user == user
    assert exception.deadline == deadline
    assert exception.id is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_str_method(django_user_model: Any) -> None:
    """Тест строкового представления AdvertisementException"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    deadline = date.today() + timedelta(days=30)

    exception = AdvertisementException.objects.create(user=user, deadline=deadline)

    assert str(exception) == str(user)
    assert str(exception) == 'testuser'


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_cascade_delete(django_user_model: Any) -> None:
    """Тест что при удалении пользователя исключение тоже удаляется"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    deadline = date.today() + timedelta(days=30)

    exception = AdvertisementException.objects.create(user=user, deadline=deadline)
    exception_id = exception.id

    # Удаляем пользователя
    user.delete()

    # Проверяем, что исключение тоже удалилось
    assert not AdvertisementException.objects.filter(id=exception_id).exists()


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_filter_by_deadline(django_user_model: Any) -> None:
    """Тест фильтрации исключений по deadline"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    user3 = django_user_model.objects.create_user(username='user3', password='password123')

    # Создаём исключения с разными датами
    past_date = date.today() - timedelta(days=10)
    today = date.today()
    future_date = date.today() + timedelta(days=10)

    AdvertisementException.objects.create(user=user1, deadline=past_date)
    AdvertisementException.objects.create(user=user2, deadline=today)
    AdvertisementException.objects.create(user=user3, deadline=future_date)

    # Фильтруем только активные (deadline >= сегодня)
    active_exceptions = AdvertisementException.objects.filter(deadline__gte=today)

    assert active_exceptions.count() == 2
    user_ids = set(active_exceptions.values_list('user__id', flat=True))
    assert user2.id in user_ids
    assert user3.id in user_ids
    assert user1.id not in user_ids


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_multiple_for_same_user(django_user_model: Any) -> None:
    """Тест что для одного пользователя может быть несколько исключений"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    deadline1 = date.today() + timedelta(days=10)
    deadline2 = date.today() + timedelta(days=20)

    exception1 = AdvertisementException.objects.create(user=user, deadline=deadline1)
    exception2 = AdvertisementException.objects.create(user=user, deadline=deadline2)

    # Проверяем, что оба исключения существуют
    assert AdvertisementException.objects.filter(user=user).count() == 2


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_query_optimization(django_user_model: Any) -> None:
    """Тест оптимизации запросов через values_list"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    deadline = date.today() + timedelta(days=30)
    AdvertisementException.objects.create(user=user1, deadline=deadline)
    AdvertisementException.objects.create(user=user2, deadline=deadline)

    # Проверяем, что values_list возвращает только ID
    user_ids = AdvertisementException.objects.filter(
        deadline__gte=date.today()
    ).values_list('user__id', flat=True)

    # Проверяем содержимое
    assert set(user_ids) == {user1.id, user2.id}


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_ordering() -> None:
    """Тест что исключения можно упорядочить по дате"""
    from django.contrib.auth.models import User

    user1 = User.objects.create_user(username='user1', password='password123')
    user2 = User.objects.create_user(username='user2', password='password123')

    deadline1 = date.today() + timedelta(days=5)
    deadline2 = date.today() + timedelta(days=15)

    AdvertisementException.objects.create(user=user1, deadline=deadline2)
    AdvertisementException.objects.create(user=user2, deadline=deadline1)

    # Упорядочиваем по deadline
    exceptions = AdvertisementException.objects.order_by('deadline')

    assert exceptions[0].user == user2
    assert exceptions[1].user == user1


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_update(django_user_model: Any) -> None:
    """Тест обновления AdvertisementException"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    old_deadline = date.today() + timedelta(days=10)

    exception = AdvertisementException.objects.create(user=user, deadline=old_deadline)

    # Обновляем deadline
    new_deadline = date.today() + timedelta(days=20)
    exception.deadline = new_deadline
    exception.save()

    # Проверяем обновление
    exception.refresh_from_db()
    assert exception.deadline == new_deadline


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_delete(django_user_model: Any) -> None:
    """Тест удаления AdvertisementException"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    deadline = date.today() + timedelta(days=30)

    exception = AdvertisementException.objects.create(user=user, deadline=deadline)
    exception_id = exception.id

    # Удаляем исключение
    exception.delete()

    # Проверяем, что удалено
    assert not AdvertisementException.objects.filter(id=exception_id).exists()

