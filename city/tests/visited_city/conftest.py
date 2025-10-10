"""
Фикстуры для тестирования функционала visited_city.
"""

from typing import Any

import pytest
from django.contrib.auth.models import User

from city.models import City, VisitedCity
from country.models import Country
from region.models import Area, Region, RegionType


def create_user(django_user_model: Any, user_id: int) -> User:
    """Создает пользователя с заданным ID."""
    return django_user_model.objects.create_user(
        id=user_id, username=f'username{user_id}', password='password'
    )


def create_country() -> Country:
    """Создает страну для тестирования."""
    return Country.objects.create(
        id=1,
        name='Россия',
        code='RU',
    )


def create_area(country: Country) -> Area:
    """Создает федеральный округ."""
    return Area.objects.create(country=country, title='Округ 1')


def create_region_type() -> RegionType:
    """Создает тип региона."""
    return RegionType.objects.create(title='область')


def create_region(area: Area, country: Country, region_type: RegionType) -> Region:
    """Создает регион."""
    return Region.objects.create(
        area=area,
        country=country,
        title='Регион 1',
        type=region_type,
        iso3166='RU-RU1',
        full_name='Регион 1 область',
    )


def create_city(region: Region, country: Country, city_id: int = 1, title: str = 'Город 1') -> City:
    """Создает город с заданными параметрами."""
    return City.objects.create(
        id=city_id,
        title=title,
        region=region,
        country=country,
        coordinate_width=1.0,
        coordinate_longitude=1.0,
    )


def create_visited_city(
    user: User,
    city: City,
    visited_city_id: int = 1,
    date_of_visit: str = '2022-02-02',
    has_magnet: bool = False,
    rating: int = 3,
    impression: str = '',
) -> VisitedCity:
    """Создает посещенный город с заданными параметрами."""
    return VisitedCity.objects.create(
        id=visited_city_id,
        user=user,
        city=city,
        date_of_visit=date_of_visit,
        has_magnet=has_magnet,
        rating=rating,
        impression=impression,
    )


@pytest.fixture
def setup(client: Any, django_user_model: Any) -> None:
    """
    Базовая фикстура для тестов.
    Создает двух пользователей, страну, округ, регион, город и одну запись посещенного города.
    """
    user1 = create_user(django_user_model, 1)
    create_user(django_user_model, 2)
    country = create_country()
    area = create_area(country)
    region_type = create_region_type()
    region = create_region(area, country, region_type)
    city = create_city(region, country)
    create_visited_city(user1, city)


@pytest.fixture
def setup_multiple_cities(client: Any, django_user_model: Any) -> None:
    """
    Расширенная фикстура для тестов с несколькими городами.
    Создает двух пользователей, страну, регион и несколько городов.
    """
    user1 = create_user(django_user_model, 1)
    user2 = create_user(django_user_model, 2)
    country = create_country()
    area = create_area(country)
    region_type = create_region_type()
    region = create_region(area, country, region_type)

    city1 = create_city(region, country, 1, 'Город 1')
    city2 = create_city(region, country, 2, 'Город 2')
    city3 = create_city(region, country, 3, 'Город 3')

    # Пользователь 1 посетил два города
    create_visited_city(user1, city1, 1, '2022-01-01', False, 3, 'Первое впечатление')
    create_visited_city(user1, city2, 2, '2022-02-02', True, 4, 'Второе впечатление')

    # Пользователь 2 посетил один город
    create_visited_city(user2, city3, 3, '2022-03-03', True, 5, 'Третье впечатление')


@pytest.fixture
def setup_with_multiple_visits(client: Any, django_user_model: Any) -> None:
    """
    Фикстура для тестов с множественными посещениями одного города.
    """
    user1 = create_user(django_user_model, 1)
    country = create_country()
    area = create_area(country)
    region_type = create_region_type()
    region = create_region(area, country, region_type)
    city = create_city(region, country)

    # Два посещения одного города в разные даты
    create_visited_city(user1, city, 1, '2022-01-01', False, 3)
    create_visited_city(user1, city, 2, '2023-01-01', True, 5)
