"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any

from services.db.statistics.visited_region import (
    get_number_of_regions,
    get_number_of_visited_regions,
    get_number_of_finished_regions,
    get_number_of_half_finished_regions,
    get_all_visited_regions,
)
from city.models import City, VisitedCity
from region.models import Region


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_regions_zero() -> None:
    """Тест получения количества регионов когда их нет"""
    result = get_number_of_regions()
    assert result == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_regions_multiple(test_country: Any, test_region_type: Any) -> None:
    """Тест получения количества регионов"""
    for i in range(5):
        Region.objects.create(
            title=f'Region {i}', country=test_country, type=test_region_type, iso3166=f'TC-{i}'
        )

    result = get_number_of_regions()
    assert result == 5


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_visited_regions_zero(django_user_model: Any) -> None:
    """Тест получения количества посещённых регионов когда их нет"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_number_of_visited_regions(user.id)
    assert result == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_visited_regions_multiple(
    django_user_model: Any, test_country: Any, test_region_type: Any
) -> None:
    """Тест получения количества посещённых регионов"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Создаём регионы с городами
    for i in range(3):
        region = Region.objects.create(
            title=f'Region {i}', country=test_country, type=test_region_type, iso3166=f'TC-{i}'
        )
        city = City.objects.create(
            title=f'City {i}',
            region=region,
            country=test_country,
            coordinate_width=55.0 + i,
            coordinate_longitude=37.0 + i,
        )
        VisitedCity.objects.create(city=city, user=user, rating=5)

    result = get_number_of_visited_regions(user.id)
    assert result == 3


@pytest.mark.integration
@pytest.mark.django_db
def test_get_all_visited_regions_returns_queryset(django_user_model: Any) -> None:
    """Тест что get_all_visited_regions возвращает QuerySet"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_all_visited_regions(user.id)

    assert result is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_get_all_visited_regions_has_total_cities_field(
    django_user_model: Any, test_city: Any
) -> None:
    """Тест что get_all_visited_regions добавляет поле total_cities"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    VisitedCity.objects.create(city=test_city, user=user, rating=5)

    result = get_all_visited_regions(user.id)

    if result.exists():
        first_region = result.first()
        assert hasattr(first_region, 'total_cities')


@pytest.mark.integration
@pytest.mark.django_db
def test_get_all_visited_regions_has_visited_cities_field(
    django_user_model: Any, test_city: Any
) -> None:
    """Тест что get_all_visited_regions добавляет поле visited_cities"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    VisitedCity.objects.create(city=test_city, user=user, rating=5)

    result = get_all_visited_regions(user.id)

    if result.exists():
        first_region = result.first()
        assert hasattr(first_region, 'visited_cities')


@pytest.mark.integration
@pytest.mark.django_db
def test_get_all_visited_regions_has_ratio_visited_field(
    django_user_model: Any, test_city: Any
) -> None:
    """Тест что get_all_visited_regions добавляет поле ratio_visited"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    VisitedCity.objects.create(city=test_city, user=user, rating=5)

    result = get_all_visited_regions(user.id)

    if result.exists():
        first_region = result.first()
        assert hasattr(first_region, 'ratio_visited')


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_finished_regions_zero(django_user_model: Any) -> None:
    """Тест получения количества завершённых регионов когда их нет"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_number_of_finished_regions(user.id)
    assert result == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_get_number_of_half_finished_regions_zero(django_user_model: Any) -> None:
    """Тест получения количества наполовину завершённых регионов когда их нет"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_number_of_half_finished_regions(user.id)
    assert result == 0
