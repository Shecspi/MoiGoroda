import csv
import json
from datetime import datetime

import openpyxl
import pytest

from account.report import CityReport
from account.serializer import TxtSerializer, CsvSerializer, XlsSerializer, JsonSerializer
from tests.account.download.create_db import (
    create_user,
    create_area,
    create_region,
    create_city,
    create_visited_city,
)


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
def test__txt_serializer__output_data(setup_db):
    report = CityReport(1).get_report()
    output = TxtSerializer().convert(report).getvalue().split('\n')

    assert (
        output[0]
        == 'Город       Регион               Дата посещения     Наличие магнита     Оценка     '
    )
    assert (
        output[1]
        == 'Город 1     Регион 1 область     2024-01-01         -                   ***        '
    )
    assert (
        output[2]
        == 'Город 2     Регион 1 область     2023-01-01         +                   *****      '
    )


@pytest.mark.django_db
def test__txt_serializer__content_type(setup_db):
    content_type = TxtSerializer().content_type()
    assert content_type == 'text/txt'


@pytest.mark.django_db
def test__txt_serializer__filetype(setup_db):
    content_type = TxtSerializer().filetype()
    assert content_type == 'txt'


@pytest.mark.django_db
def test__csv_serializer__output_data(setup_db):
    report = CityReport(1).get_report()
    buffer = CsvSerializer().convert(report).getvalue().strip().split('\n')
    reader = csv.reader(buffer, delimiter=',', lineterminator='\n')
    correct_results = (
        ['Город', 'Регион', 'Дата посещения', 'Наличие магнита', 'Оценка'],
        ['Город 1', 'Регион 1 область', '2024-01-01', '-', '***'],
        ['Город 2', 'Регион 1 область', '2023-01-01', '+', '*****'],
    )
    for index, row in enumerate(reader):
        assert row == correct_results[index]


@pytest.mark.django_db
def test__csv_serializer__content_type(setup_db):
    content_type = CsvSerializer().content_type()
    assert content_type == 'text/csv'


@pytest.mark.django_db
def test__csv_serializer__filetype(setup_db):
    content_type = CsvSerializer().filetype()
    assert content_type == 'csv'


@pytest.mark.django_db
def test__json_serializer__output_data(setup_db):
    report = CityReport(1).get_report()
    buffer = JsonSerializer().convert(report).getvalue()
    reader = json.loads(buffer)
    correct_results = (
        ['Город', 'Регион', 'Дата посещения', 'Наличие магнита', 'Оценка'],
        ['Город 1', 'Регион 1 область', '2024-01-01', '-', '***'],
        ['Город 2', 'Регион 1 область', '2023-01-01', '+', '*****'],
    )
    for index, row in enumerate(reader):
        assert row == correct_results[index]


@pytest.mark.django_db
def test__json_serializer__content_type(setup_db):
    content_type = JsonSerializer().content_type()
    assert content_type == 'application/json'


@pytest.mark.django_db
def test__json_serializer__filetype(setup_db):
    content_type = JsonSerializer().filetype()
    assert content_type == 'json'


@pytest.mark.django_db
def test__xls_serializer__output_data(setup_db):
    report = CityReport(1).get_report()
    buffer = XlsSerializer().convert(report)
    workbook = openpyxl.load_workbook(buffer)
    sheet = workbook['Sheet']
    correct_results = (
        ['Город', 'Регион', 'Дата посещения', 'Наличие магнита', 'Оценка'],
        ['Город 1', 'Регион 1 область', '2024-01-01', '-', '***'],
        ['Город 2', 'Регион 1 область', '2023-01-01', '+', '*****'],
    )
    for index_row, value_row in enumerate(correct_results):
        for index_column, value_column in enumerate(value_row):
            assert sheet.cell(row=index_row + 1, column=index_column + 1).value == value_column


@pytest.mark.django_db
def test__xls_serializer__content_type(setup_db):
    content_type = XlsSerializer().content_type()
    assert content_type == 'application/vnd.ms-excel'


@pytest.mark.django_db
def test__xls_serializer__filetype(setup_db):
    content_type = XlsSerializer().filetype()
    assert content_type == 'xls'
