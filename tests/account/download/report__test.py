from datetime import datetime

import pytest

from django.contrib.auth.models import User

from account.report import CityReport, RegionReport, AreaReport
from city.models import City, VisitedCity
from region.models import Region, Area


def create_user(django_user_model):
    return django_user_model.objects.create_user(id=1, username='username', password='password')


def create_area(num: int) -> list[Area]:
    return [
        Area.objects.create(id=1, title=f'Округ {i}') for i in range(1, num + 1)
    ]


def create_region(num: int, area: Area) -> list[Region]:
    return [
        Region.objects.create(
            id=1,
            area=area,
            title=f'Регион {i}',
            type='область',
            iso3166=f'RU-RU{i}'
        ) for i in range(1, num + 1)
    ]


def create_city(num: int, region: Region) -> list[City]:
    return [
        City.objects.create(
            id=i,
            title=f'Город {i}',
            region=region,
            coordinate_width=1,
            coordinate_longitude=1
        ) for i in range(1, num + 1)
    ]


def create_visited_city(
        region: Region,
        user: User,
        city: City,
        date_of_visit: datetime,
        has_magnet: bool,
        rating: int
) -> VisitedCity:
    return VisitedCity.objects.create(
        user=user,
        region=region,
        city=city,
        date_of_visit=date_of_visit,
        has_magnet=has_magnet,
        rating=rating
    )


@pytest.fixture
def setup_db(client, django_user_model):
    user = create_user(django_user_model)
    area = create_area(1)
    region = create_region(1, area[0])
    city = create_city(2, region[0])
    date_of_visit_1 = datetime.strptime('2024-01-01', '%Y-%m-%d')
    date_of_visit_2 = datetime.strptime('2023-01-01', '%Y-%m-%d')
    create_visited_city(region[0], user, city[0], date_of_visit_1, False, 3)
    create_visited_city(region[0], user, city[1], date_of_visit_2, True, 5)


@pytest.mark.django_db
def test__city_report(setup_db):
    report = CityReport(1).get_report()

    assert report[0] == ('Город', 'Регион', 'Дата посещения', 'Наличие магнита', 'Оценка')
    assert report[1] == ('Город 1', 'Регион 1 область', '2024-01-01', '-', '***')
    assert report[2] == ('Город 2', 'Регион 1 область', '2023-01-01', '+', '*****')


@pytest.mark.django_db
def test__region_report(setup_db):
    report = RegionReport(1).get_report()

    assert report[0] == (
        'Регион', 'Всего городов', 'Посещено городов, шт', 'Посещено городов, %', 'Осталось посетить, шт'
    )
    assert report[1] == ('Регион 1 область', '2', '2', '100%', '0')


@pytest.mark.django_db
def test__area_report(setup_db):
    report = AreaReport(1).get_report()

    assert report[0] == (
        'Федеральный округ', 'Всего регионов, шт', 'Посещено регионов, шт',
        'Посещено регионов, %', 'Осталось посетить, шт'
    )
    assert report[1] == ('Округ 1', '1', '1', '100%', '0')
