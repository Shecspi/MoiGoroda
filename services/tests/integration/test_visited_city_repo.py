"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any

from services.db.visited_city_repo import get_visited_city, get_number_of_visited_cities
from city.models import City, VisitedCity


@pytest.mark.integration
@pytest.mark.django_db
def test_get_visited_city_exists(django_user_model: Any, test_city: Any) -> None:
    """Тест получения существующего посещённого города"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    visited_city = VisitedCity.objects.create(city=test_city, user=user, rating=5)

    result = get_visited_city(user.id, visited_city.id)

    assert result is not False
    assert isinstance(result, VisitedCity)
    assert result.id == visited_city.id


@pytest.mark.integration
@pytest.mark.django_db
def test_get_visited_city_not_exists(django_user_model: Any) -> None:
    """Тест получения несуществующего посещённого города"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_visited_city(user.id, 99999)

    assert result is False


@pytest.mark.integration
@pytest.mark.django_db
def test_get_visited_city_wrong_user(django_user_model: Any, test_city: Any) -> None:
    """Тест получения посещённого города другого пользователя"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    visited_city = VisitedCity.objects.create(city=test_city, user=user1, rating=5)

    result = get_visited_city(user2.id, visited_city.id)

    assert result is False


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_visited_cities_zero(django_user_model: Any) -> None:
    """Тест получения количества посещённых городов для пользователя без городов"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_number_of_visited_cities(user.id)

    assert result == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_visited_cities_one(django_user_model: Any, test_city: Any) -> None:
    """Тест получения количества посещённых городов для пользователя с одним городом"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    VisitedCity.objects.create(city=test_city, user=user, rating=5)

    result = get_number_of_visited_cities(user.id)

    assert result == 1


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_visited_cities_multiple(
    django_user_model: Any, test_region: Any, test_country: Any
) -> None:
    """Тест получения количества посещённых городов для пользователя с несколькими городами"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    for i in range(5):
        city = City.objects.create(
            title=f'City {i}',
            region=test_region,
            country=test_country,
            coordinate_width=55.0 + i,
            coordinate_longitude=37.0 + i,
        )
        VisitedCity.objects.create(city=city, user=user, rating=5)

    result = get_number_of_visited_cities(user.id)

    assert result == 5


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_visited_cities_different_users(
    django_user_model: Any, test_region: Any, test_country: Any
) -> None:
    """Тест что количество посещённых городов изолировано между пользователями"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    # User1 посещает 3 города
    for i in range(3):
        city = City.objects.create(
            title=f'City {i}',
            region=test_region,
            country=test_country,
            coordinate_width=55.0 + i,
            coordinate_longitude=37.0 + i,
        )
        VisitedCity.objects.create(city=city, user=user1, rating=5)

    # User2 посещает 2 города
    for i in range(3, 5):
        city = City.objects.create(
            title=f'City {i}',
            region=test_region,
            country=test_country,
            coordinate_width=55.0 + i,
            coordinate_longitude=37.0 + i,
        )
        VisitedCity.objects.create(city=city, user=user2, rating=5)

    result1 = get_number_of_visited_cities(user1.id)
    result2 = get_number_of_visited_cities(user2.id)

    assert result1 == 3
    assert result2 == 2
