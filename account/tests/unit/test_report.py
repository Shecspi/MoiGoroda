"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import date

import pytest
from typing import Any

from account.report import CityReport, RegionReport, AreaReport


# ===== Тесты для CityReport =====


@pytest.mark.unit
def test_city_report_with_grouped_cities(mocker: Any) -> None:
    """Тест CityReport с группировкой городов"""
    # Мокаем зависимости
    mock_get_unique_cities = mocker.patch('account.report.get_unique_visited_cities')
    mock_apply_sort = mocker.patch('account.report.apply_sort_to_queryset')

    # Подготовка фейковых объектов
    fake_city_1 = mocker.MagicMock()
    fake_city_1.city.title = 'Город 1'
    fake_city_1.city.region.__str__ = mocker.Mock(return_value='Регион 1 область')
    fake_city_1.city.country.__str__ = mocker.Mock(return_value='Россия')
    fake_city_1.number_of_visits = 1
    fake_city_1.first_visit_date = date(2024, 1, 1)
    fake_city_1.last_visit_date = date(2024, 1, 1)
    fake_city_1.has_souvenir = False
    fake_city_1.average_rating = 3.0

    fake_city_2 = mocker.MagicMock()
    fake_city_2.city.title = 'Город 2'
    fake_city_2.city.region.__str__ = mocker.Mock(return_value='Регион 2 область')
    fake_city_2.city.country.__str__ = mocker.Mock(return_value='Россия')
    fake_city_2.number_of_visits = 2
    fake_city_2.first_visit_date = date(2022, 1, 1)
    fake_city_2.last_visit_date = date(2023, 1, 1)
    fake_city_2.has_souvenir = True
    fake_city_2.average_rating = 4.0

    # Настраиваем возвращаемые значения моков
    mock_get_unique_cities.return_value = [fake_city_1, fake_city_2]
    mock_apply_sort.return_value = [fake_city_1, fake_city_2]

    # Выполняем тестируемый код с группировкой
    report = CityReport(1, group_city=True).get_report()

    # Проверка результата
    assert report == [
        (
            'Город',
            'Регион',
            'Страна',
            'Количество посещений',
            'Дата первого посещения',
            'Дата последнего посещения',
            'Наличие сувенира',
            'Средняя оценка',
        ),
        ('Город 1', 'Регион 1 область', 'Россия', 1, '2024-01-01', '2024-01-01', '-', 3.0),
        ('Город 2', 'Регион 2 область', 'Россия', 2, '2022-01-01', '2023-01-01', '+', 4.0),
    ]

    mock_get_unique_cities.assert_called_once_with(1)
    mock_apply_sort.assert_called_once_with([fake_city_1, fake_city_2], 'last_visit_date_down')


@pytest.mark.unit
def test_city_report_without_grouping(mocker: Any) -> None:
    """Тест CityReport без группировки городов"""
    mock_get_all_cities = mocker.patch('account.report.get_all_visited_cities')

    # Подготовка фейковых объектов
    fake_city = mocker.MagicMock()
    fake_city.city.title = 'Город 1'
    fake_city.city.region.__str__ = mocker.Mock(return_value='Регион 1 область')
    fake_city.city.country.__str__ = mocker.Mock(return_value='Россия')
    fake_city.date_of_visit = date(2024, 1, 1)
    fake_city.has_magnet = True
    fake_city.rating = 5

    # Настраиваем мок QuerySet
    mock_queryset = mocker.MagicMock()
    mock_queryset.order_by.return_value = [fake_city]
    mock_get_all_cities.return_value = mock_queryset

    # Выполняем тестируемый код без группировки
    report = CityReport(1, group_city=False).get_report()

    # Проверка результата
    assert report == [
        ('Город', 'Регион', 'Страна', 'Дата посещения', 'Наличие сувенира', 'Оценка'),
        ('Город 1', 'Регион 1 область', 'Россия', '2024-01-01', '+', 5),
    ]

    mock_get_all_cities.assert_called_once_with(1)


@pytest.mark.unit
def test_city_report_no_visited_cities(mocker: Any) -> None:
    """Тест CityReport без посещённых городов"""
    mock_get_all_cities = mocker.patch('account.report.get_all_visited_cities')

    # Мокаем пустой QuerySet
    empty_queryset = mocker.MagicMock()
    empty_queryset.order_by.return_value = []
    mock_get_all_cities.return_value = empty_queryset

    # Выполнение отчёта
    report = CityReport(1).get_report()

    # Ожидаем, что отчёт будет содержать только заголовки
    assert report == [
        ('Город', 'Регион', 'Страна', 'Дата посещения', 'Наличие сувенира', 'Оценка'),
    ]


@pytest.mark.unit
def test_city_report_city_without_region(mocker: Any) -> None:
    """Тест CityReport с городом без региона"""
    mock_get_all_cities = mocker.patch('account.report.get_all_visited_cities')

    fake_city = mocker.MagicMock()
    fake_city.city.title = 'Город без региона'
    fake_city.city.region = None
    fake_city.city.country.__str__ = mocker.Mock(return_value='Россия')
    fake_city.date_of_visit = date(2024, 1, 1)
    fake_city.has_magnet = False
    fake_city.rating = None

    mock_queryset = mocker.MagicMock()
    mock_queryset.order_by.return_value = [fake_city]
    mock_get_all_cities.return_value = mock_queryset

    report = CityReport(1).get_report()

    assert report[1][1] == 'Нет региона'
    assert report[1][5] == ''  # Рейтинг пустой


@pytest.mark.unit
def test_city_report_without_dates(mocker: Any) -> None:
    """Тест CityReport с городом без дат посещения"""
    mock_get_unique_cities = mocker.patch('account.report.get_unique_visited_cities')
    mock_apply_sort = mocker.patch('account.report.apply_sort_to_queryset')

    fake_city = mocker.MagicMock()
    fake_city.city.title = 'Город'
    fake_city.city.region.__str__ = mocker.Mock(return_value='Регион')
    fake_city.city.country.__str__ = mocker.Mock(return_value='Россия')
    fake_city.number_of_visits = 1
    fake_city.first_visit_date = None
    fake_city.last_visit_date = None
    fake_city.has_souvenir = False
    fake_city.average_rating = None

    mock_get_unique_cities.return_value = [fake_city]
    mock_apply_sort.return_value = [fake_city]

    report = CityReport(1, group_city=True).get_report()

    assert report[1][4] == 'Не указана'  # first_visit_date
    assert report[1][5] == 'Не указана'  # last_visit_date
    assert report[1][7] == ''  # average_rating


# ===== Тесты для RegionReport =====


@pytest.mark.unit
def test_region_report_with_regions(mocker: Any) -> None:
    """Тест RegionReport с регионами"""
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    fake_region = mocker.MagicMock()
    fake_region.__str__.return_value = 'Регион 1 область'
    fake_region.num_total = 2
    fake_region.num_visited = 2

    mock_get_regions.return_value = [fake_region]

    report = RegionReport(1).get_report()

    assert report == [
        (
            'Регион',
            'Всего городов',
            'Посещено городов, шт',
            'Посещено городов, %',
            'Осталось посетить, шт',
        ),
        ('Регион 1 область', 2, 2, '100%', 0),
    ]

    mock_get_regions.assert_called_once_with(1)


@pytest.mark.unit
def test_region_report_empty_regions(mocker: Any) -> None:
    """Тест RegionReport с пустым списком регионов"""
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')
    mock_get_regions.return_value = []

    report = RegionReport(1).get_report()

    assert report == [
        (
            'Регион',
            'Всего городов',
            'Посещено городов, шт',
            'Посещено городов, %',
            'Осталось посетить, шт',
        ),
    ]


@pytest.mark.unit
def test_region_report_no_visited_cities(mocker: Any) -> None:
    """Тест RegionReport с регионом без посещённых городов"""
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    fake_region = mocker.MagicMock()
    fake_region.__str__.return_value = 'Регион 2 область'
    fake_region.num_total = 2
    fake_region.num_visited = 0

    mock_get_regions.return_value = [fake_region]

    report = RegionReport(1).get_report()

    assert report == [
        (
            'Регион',
            'Всего городов',
            'Посещено городов, шт',
            'Посещено городов, %',
            'Осталось посетить, шт',
        ),
        ('Регион 2 область', 2, 0, '0%', 2),
    ]


@pytest.mark.unit
def test_region_report_division_by_zero(mocker: Any) -> None:
    """Тест RegionReport с делением на ноль"""
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    fake_region = mocker.MagicMock()
    fake_region.__str__.return_value = 'Регион 3 область'
    fake_region.num_total = 0
    fake_region.num_visited = 0

    mock_get_regions.return_value = [fake_region]

    report = RegionReport(1).get_report()

    assert report[1][3] == '0%'


@pytest.mark.unit
def test_region_report_multiple_regions(mocker: Any) -> None:
    """Тест RegionReport с несколькими регионами"""
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    fake_region_1 = mocker.MagicMock()
    fake_region_1.__str__.return_value = 'Регион 1 область'
    fake_region_1.num_total = 2
    fake_region_1.num_visited = 2

    fake_region_2 = mocker.MagicMock()
    fake_region_2.__str__.return_value = 'Регион 2 область'
    fake_region_2.num_total = 3
    fake_region_2.num_visited = 1

    mock_get_regions.return_value = [fake_region_1, fake_region_2]

    report = RegionReport(1).get_report()

    assert len(report) == 3
    assert report[1] == ('Регион 1 область', 2, 2, '100%', 0)
    assert report[2] == ('Регион 2 область', 3, 1, '33%', 2)


@pytest.mark.unit
def test_region_report_percentage_rounding(mocker: Any) -> None:
    """Тест округления процентов в RegionReport"""
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    fake_region = mocker.MagicMock()
    fake_region.__str__.return_value = 'Регион 4 область'
    fake_region.num_total = 2
    fake_region.num_visited = 1

    mock_get_regions.return_value = [fake_region]

    report = RegionReport(1).get_report()

    assert report[1][3] == '50%'


# ===== Тесты для AreaReport =====


@pytest.mark.unit
def test_area_report_with_areas(mocker: Any) -> None:
    """Тест AreaReport с федеральными округами"""
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    fake_area = mocker.MagicMock()
    fake_area.title = 'Округ 1'
    fake_area.total_regions = 1
    fake_area.visited_regions = 1

    mock_get_areas.return_value = [fake_area]

    report = AreaReport(1).get_report()

    assert report == [
        (
            'Федеральный округ',
            'Всего регионов, шт',
            'Посещено регионов, шт',
            'Посещено регионов, %',
            'Осталось посетить, шт',
        ),
        ('Округ 1', 1, 1, '100%', 0),
    ]


@pytest.mark.unit
def test_area_report_empty_area(mocker: Any) -> None:
    """Тест AreaReport с пустым списком округов"""
    mock_get_areas = mocker.patch('account.report.get_visited_areas')
    mock_get_areas.return_value = []

    report = AreaReport(1).get_report()

    assert report == [
        (
            'Федеральный округ',
            'Всего регионов, шт',
            'Посещено регионов, шт',
            'Посещено регионов, %',
            'Осталось посетить, шт',
        ),
    ]


@pytest.mark.unit
def test_area_report_no_visited_regions(mocker: Any) -> None:
    """Тест AreaReport с округом без посещённых регионов"""
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    fake_area = mocker.MagicMock()
    fake_area.title = 'Округ 2'
    fake_area.total_regions = 2
    fake_area.visited_regions = 0

    mock_get_areas.return_value = [fake_area]

    report = AreaReport(1).get_report()

    assert report[1] == ('Округ 2', 2, 0, '0%', 2)


@pytest.mark.unit
def test_area_report_zero_division(mocker: Any) -> None:
    """Тест AreaReport с делением на ноль"""
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    fake_area = mocker.MagicMock()
    fake_area.title = 'Округ 3'
    fake_area.total_regions = 0
    fake_area.visited_regions = 0

    mock_get_areas.return_value = [fake_area]

    report = AreaReport(1).get_report()

    assert report[1][3] == '0%'


@pytest.mark.unit
def test_area_report_rounding_percentage(mocker: Any) -> None:
    """Тест округления процентов в AreaReport"""
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    fake_area = mocker.MagicMock()
    fake_area.title = 'Округ 4'
    fake_area.total_regions = 3
    fake_area.visited_regions = 2

    mock_get_areas.return_value = [fake_area]

    report = AreaReport(1).get_report()

    assert report[1][3] == '67%'


@pytest.mark.unit
def test_area_report_multiple_areas(mocker: Any) -> None:
    """Тест AreaReport с несколькими округами"""
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    fake_area_1 = mocker.MagicMock()
    fake_area_1.title = 'Округ 1'
    fake_area_1.total_regions = 2
    fake_area_1.visited_regions = 1

    fake_area_2 = mocker.MagicMock()
    fake_area_2.title = 'Округ 2'
    fake_area_2.total_regions = 2
    fake_area_2.visited_regions = 0

    mock_get_areas.return_value = [fake_area_1, fake_area_2]

    report = AreaReport(1).get_report()

    assert len(report) == 3
    assert report[1] == ('Округ 1', 2, 1, '50%', 1)
    assert report[2] == ('Округ 2', 2, 0, '0%', 2)


# ===== Тесты на общие характеристики =====


@pytest.mark.unit
def test_all_reports_implement_interface() -> None:
    """Тест что все отчёты реализуют интерфейс Report"""
    reports = [CityReport(1), RegionReport(1), AreaReport(1)]

    for report in reports:
        assert hasattr(report, 'get_report')
        assert callable(report.get_report)


@pytest.mark.unit
def test_reports_accept_user_id() -> None:
    """Тест что все отчёты принимают user_id"""
    city_report = CityReport(123)
    region_report = RegionReport(456)
    area_report = AreaReport(789)

    assert city_report.user_id == 123
    assert region_report.user_id == 456
    assert area_report.user_id == 789


@pytest.mark.unit
def test_city_report_accepts_group_city_parameter() -> None:
    """Тест что CityReport принимает параметр group_city"""
    report_with_grouping = CityReport(1, group_city=True)
    report_without_grouping = CityReport(1, group_city=False)
    report_default = CityReport(1)

    assert report_with_grouping.group_city is True
    assert report_without_grouping.group_city is False
    assert report_default.group_city is False
