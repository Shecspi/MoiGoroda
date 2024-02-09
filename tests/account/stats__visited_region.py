from typing import Sequence

import pytest
from datetime import datetime

from city.models import City, VisitedCity
from region.models import Area, Region
from services.db.stats_regions import *


def create_user(django_user_model):
    return django_user_model.objects.create_user(id=1, username='username', password='password')


def create_area():
    return Area.objects.create(title='Округ 1')


def create_region(area):
    return Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')


def create_city(number_of_cities, region):
    """
    Добавляет в базу данных города и возвращает список с инстансами созданных городов.
    """
    cities = []

    for num in range(number_of_cities):
        cities.append(
            City.objects.create(
                id=num,
                title=f'Город {num + 1}',
                region=region,
                coordinate_width=1,
                coordinate_longitude=1
            ))

    return cities


def create_visited_city(
        number_of_cities: int,  # Количество создаваемых посещённых городов
        region: int,  # Регион, в который будут добавляться посещаемые города
        user: int,  # Пользователь, которому будут добавляться посещяемые города
        cities: Sequence,  # Последовательность инстансов из таблицы City
        date_of_visit: Sequence[str]  # Последовательность дат посещения города (её длина равна number_of_cities)
):
    """
    Добавляет в базу данных посещённые города.
    """
    for num in range(number_of_cities):
        VisitedCity.objects.create(
            user=user,
            region=region,
            city=cities[num],
            date_of_visit=date_of_visit[num],
            has_magnet=False,
            rating=3
        )


@pytest.fixture
def setup(client, django_user_model):
    user = create_user(django_user_model)
    area = create_area()
    region = create_region(area)
    cities = create_city(17, region)

    date_of_visit = [f'{datetime.now().year}-01-01' for _ in range(3)]
    date_of_visit += [f'{datetime.now().year - 1}-01-01' for _ in range(5)]
    date_of_visit += [f'{datetime.now().year - 2}-01-01' for _ in range(4)]
    create_visited_city(12, region, user, cities, date_of_visit=date_of_visit)


@pytest.mark.django_db
def test__get_number_of_visited_regions(setup):
    assert get_number_of_visited_regions(1) == 1


@pytest.mark.django_db
def test__get_number_of_visited_regions_for_not_existing_user(setup):
    assert get_number_of_visited_regions(2) == 0
