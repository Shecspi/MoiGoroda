"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from datetime import date

from services.db.statistics.visited_city import (
    get_number_of_cities,
    get_number_of_visited_cities,
    get_number_of_not_visited_cities,
    get_number_of_visited_cities_by_year,
)
from city.models import City, VisitedCity


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_cities_zero() -> None:
    """Тест получения количества городов когда их нет"""
    result = get_number_of_cities()
    assert result == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_cities_multiple(test_region: Any, test_country: Any) -> None:
    """Тест получения количества городов"""
    for i in range(5):
        City.objects.create(
            title=f'City {i}',
            region=test_region,
            country=test_country,
            coordinate_width=55.0 + i,
            coordinate_longitude=37.0 + i,
        )

    result = get_number_of_cities()
    assert result == 5


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_visited_cities_zero(django_user_model: Any) -> None:
    """Тест получения количества посещённых городов когда их нет"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_number_of_visited_cities(user.id)
    assert result == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_visited_cities_multiple(
    django_user_model: Any, test_region: Any, test_country: Any
) -> None:
    """Тест получения количества посещённых городов"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    for i in range(3):
        city = City.objects.create(
            title=f'City {i}',
            region=test_region,
            country=test_country,
            coordinate_width=55.0 + i,
            coordinate_longitude=37.0 + i,
        )
        VisitedCity.objects.create(city=city, user=user, rating=5)

    result = get_number_of_visited_cities(user.id)
    assert result == 3


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_not_visited_cities(
    django_user_model: Any, test_region: Any, test_country: Any
) -> None:
    """Тест получения количества непосещённых городов"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Создаём 10 городов
    for i in range(10):
        City.objects.create(
            title=f'City {i}',
            region=test_region,
            country=test_country,
            coordinate_width=55.0 + i,
            coordinate_longitude=37.0 + i,
        )

    # Пользователь посещает 3 города
    for i in range(3):
        city = City.objects.get(title=f'City {i}')
        VisitedCity.objects.create(city=city, user=user, rating=5)

    result = get_number_of_not_visited_cities(user.id)
    assert result == 7


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_visited_cities_by_year(
    django_user_model: Any, test_region: Any, test_country: Any
) -> None:
    """Тест получения количества посещённых городов за год"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Создаём города
    for i in range(5):
        city = City.objects.create(
            title=f'City {i}',
            region=test_region,
            country=test_country,
            coordinate_width=55.0 + i,
            coordinate_longitude=37.0 + i,
        )
        VisitedCity.objects.create(city=city, user=user, rating=5, date_of_visit=date(2024, 1, 1))

    # Создаём города с другой датой
    for i in range(3):
        city = City.objects.create(
            title=f'City {i + 5}',
            region=test_region,
            country=test_country,
            coordinate_width=55.0 + i + 5,
            coordinate_longitude=37.0 + i + 5,
        )
        VisitedCity.objects.create(city=city, user=user, rating=5, date_of_visit=date(2023, 1, 1))

    result_2024 = get_number_of_visited_cities_by_year(user.id, 2024)
    result_2023 = get_number_of_visited_cities_by_year(user.id, 2023)

    assert result_2024 == 5
    assert result_2023 == 3


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_visited_cities_by_year_none(django_user_model: Any) -> None:
    """Тест получения количества посещённых городов за год когда их нет"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_number_of_visited_cities_by_year(user.id, 2024)
    assert result == 0
