from datetime import datetime

import pytest

from account.report import CityReport
from account.serializer import TxtSerializer
from tests.account.download.create_db import create_user, create_area, create_region, create_city, create_visited_city


@pytest.fixture
def setup_db(django_user_model):
    user = create_user(django_user_model)
    area = create_area(1)
    region = create_region(1, area[0])
    city = create_city(2, region[0])
    date_of_visit_1 = datetime.strptime('2024-01-01', '%Y-%m-%d')
    date_of_visit_2 = datetime.strptime('2023-01-01', '%Y-%m-%d')
    create_visited_city(region[0], user, city[0], date_of_visit_1, False, 3)
    create_visited_city(region[0], user, city[1], date_of_visit_2, True, 5)


@pytest.mark.django_db
def test__txt_serializer__output_data(setup_db):
    report = CityReport(1).get_report()
    output = TxtSerializer().convert(report).getvalue().split('\n')

    assert output[0] == 'Город       Регион               Дата посещения     Наличие магнита     Оценка     '
    assert output[1] == 'Город 1     Регион 1 область     2024-01-01         -                   ***        '
    assert output[2] == 'Город 2     Регион 1 область     2023-01-01         +                   *****      '


@pytest.mark.django_db
def test__txt_serializer__content_type(setup_db):
    report = CityReport(1).get_report()
    content_type = TxtSerializer().content_type()

    assert content_type == 'text/txt'


@pytest.mark.django_db
def test__txt_serializer__filetype(setup_db):
    report = CityReport(1).get_report()
    content_type = TxtSerializer().filetype()

    assert content_type == 'txt'
