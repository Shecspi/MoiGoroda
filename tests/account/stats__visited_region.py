from collections import defaultdict
from typing import Sequence, Mapping

import pytest
from datetime import datetime

from django.contrib.auth.models import User

from city.models import City, VisitedCity
from region.models import Area, Region
from services.db.statistics_of_visited_regions import *

from services.db.statistics_of_visited_regions import get_all_visited_regions


def create_user(django_user_model):
    return django_user_model.objects.create_user(id=1, username='username', password='password')


def create_area() -> Area:
    return Area.objects.create(title='Округ 1')


def create_region(area: Area) -> list[Region]:
    """
    Создаёт number_of_regions регионов и возвращает список с экземплярами модели Region.
    Всего создаётся 15 регионов.
    """
    regions = []
    for i in range(1, 16):
        regions.append(
            Region.objects.create(id=i, area=area, title=f'Регион {i}', type='область', iso3166=f'RU-RU{i}')
        )
    return regions


def create_city(regions: Sequence[Region]) -> dict[int, list[City]]:
    """
    Добавляет в базу данных 3 города для каждого региона и возвращает список с инстансами созданных городов.
    Для каждого города создаётся связь с Region, указанным в regions.
    Для каждого из 15 регионов создаётся по 3 города.
    """
    cities = defaultdict(list)
    city_id = 1

    for index, region in enumerate(regions):
        for _ in range(3):
            cities[region.id].append(
                City.objects.create(
                    id=city_id,
                    title=f'Город {city_id}',
                    region=region,
                    coordinate_width=1,
                    coordinate_longitude=1
                )
            )
            city_id += 1

    return cities


def create_visited_city(
        user: User,
        cities: Mapping[int, list[City]]
):
    """
    Добавляет в базу данных посещённые города.
    Для регионов с ID 1, 5, 9 и 13 добавляется 1 посещённый город. Таких 4 региона.
    Для регионов с ID 2, 6, 10 и 14 добавляется 2 посещённых города. Таких 4 региона.
    Для регионов с ID 3, 7, 11 и 15 добавляется 3 посещённых города. Таких 4 региона.
    Для регионов с ID 4, 8, 12 посещённые города не добавляются. Таких 3 региона.
    """
    i = 0
    for item in cities.items():
        # Для каждого нечётного Region ID добавляем 2 города, а для чётного - 1
        region_id = item[0]
        sequence_of_cities = item[1]

        # Количество посещённых в регионе городов (может принимать значения 1, 2, 3)
        number_of_visited_cities_in_region = region_id % 4

        for city in sequence_of_cities[:number_of_visited_cities_in_region]:
            VisitedCity.objects.create(
                user=user,
                region=Region.objects.get(id=region_id),
                city=city,
                date_of_visit=f'{datetime.now().year}-01-01',
                has_magnet=False,
                rating=3
            )
        i += 1


@pytest.fixture
def setup(client, django_user_model):
    user = create_user(django_user_model)
    area = create_area()
    regions = create_region(area)
    cities = create_city(regions)
    create_visited_city(user, cities)


@pytest.mark.django_db
def test__get_number_of_regions(setup):
    """
    Проверяет, что get_number_of_regions() возвращает корректное общее количество регионов.
    """
    assert get_number_of_regions() == 15


@pytest.mark.django_db
def test__get_all_visited_regions__contains(setup):
    """
    Проверяет, что get_all_visited_regions() возвращает все посещённые регионы, а непосещённые - не возвращает.
    """
    regions = tuple(get_all_visited_regions(1).values_list('title', flat=True))

    assert 'Регион 1' in regions
    assert 'Регион 2' in regions
    assert 'Регион 3' in regions
    assert 'Регион 5' in regions
    assert 'Регион 6' in regions
    assert 'Регион 7' in regions
    assert 'Регион 9' in regions
    assert 'Регион 10' in regions
    assert 'Регион 11' in regions
    assert 'Регион 13' in regions
    assert 'Регион 14' in regions
    assert 'Регион 15' in regions
    assert 'Регион 4' not in regions
    assert 'Регион 8' not in regions
    assert 'Регион 12' not in regions


@pytest.mark.django_db
def test__get_all_visited_regions__order(setup):
    """
    Проверяет сортировку, которая применяется в get_all_visited_regions().
    В начале должны идти регионы с самым большим количеством посещённых городов и постепенно уменьшаться.
    """
    regions = tuple(get_all_visited_regions(1).values_list('title', flat=True))

    assert 'Регион 3' in regions[0:4]
    assert 'Регион 7' in regions[0:4]
    assert 'Регион 11' in regions[0:4]
    assert 'Регион 15' in regions[0:4]
    assert 'Регион 2' in regions[4:8]
    assert 'Регион 6' in regions[4:8]
    assert 'Регион 10' in regions[4:8]
    assert 'Регион 14' in regions[4:8]
    assert 'Регион 1' in regions[8:12]
    assert 'Регион 5' in regions[8:12]
    assert 'Регион 9' in regions[8:12]
    assert 'Регион 13' in regions[8:12]


@pytest.mark.django_db
def test__get_all_visited_regions__total_cities(setup):
    """
    Проверяет поле `total_cities` в QuerySet, возвращаемом функцией get_all_visited_regions
    """
    regions = get_all_visited_regions(1)

    for region in regions:
        assert region.total_cities == 3


@pytest.mark.django_db
def test__get_all_visited_regions__visited_cities(setup):
    """
    Проверяет поле `visited_cities` в QuerySet, возвращаемом функцией get_all_visited_regions
    """
    regions = get_all_visited_regions(1)

    numbers = [3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1]
    for index, region in enumerate(regions):
        assert region.visited_cities == numbers[index]


@pytest.mark.django_db
def test__get_all_visited_regions__ratio_visited(setup):
    """
    Проверяет поле `ratio_visited` в QuerySet, возвращаемом функцией get_all_visited_regions
    """
    regions = get_all_visited_regions(1)

    numbers = [100, 100, 100, 100, 2, 2, 2, 2, 1, 1, 1, 1]
    for index, region in enumerate(regions):
        assert region.ratio_visited == (region.visited_cities / region.total_cities) * 100


@pytest.mark.django_db
def test__get_number_of_visited_regions__has_visited_regions(setup):
    """
    Проверяет корректность работы функции get_number_of_visited_regions.
    Для пользователя, у которого имеются посещённые регионы, должно возвращаться их число.
    """
    assert get_number_of_visited_regions(1) == 12


@pytest.mark.django_db
def test__get_number_of_visited_regions__has_no_visited_regions(setup):
    """
    Проверяет корректность работы функции get_number_of_visited_regions.
    Для пользователя, у которого нет посещённых регионов, должен возвращаться 0..
    """
    assert get_number_of_visited_regions(2) == 0


@pytest.mark.django_db
def test__get_number_of_finished_regions(setup):
    assert get_number_of_finished_regions(1) == 4
