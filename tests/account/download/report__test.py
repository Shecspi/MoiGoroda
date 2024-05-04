from datetime import datetime

import pytest

from account.report import CityReport, RegionReport, AreaReport
from tests.account.download.create_db import create_user, create_area, create_region, create_city, create_visited_city


@pytest.fixture
def setup_db(django_user_model):
    user = create_user(django_user_model, 1)
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
