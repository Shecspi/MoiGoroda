from datetime import date

import pytest

from account.report import CityReport, RegionReport, AreaReport


@pytest.mark.django_db
def test__city_report(mocker):
    # Мокаем зависимости
    mock_get_all_visited_cities = mocker.patch('account.report.get_all_visited_cities')
    mock_apply_sort = mocker.patch('account.report.apply_sort_to_queryset')

    # Подготовка фейковых объектов
    fake_city_1 = mocker.MagicMock()
    fake_city_1.city.title = 'Город 1'
    fake_city_1.region.__str__.return_value = 'Регион 1 область'
    fake_city_1.number_of_visits = 1
    fake_city_1.first_visit_date = date(2024, 1, 1)
    fake_city_1.last_visit_date = date(2024, 1, 1)
    fake_city_1.has_souvenir = False
    fake_city_1.average_rating = 3.0

    fake_city_2 = mocker.MagicMock()
    fake_city_2.city.title = 'Город 2'
    fake_city_2.region.__str__.return_value = 'Регион 1 область'
    fake_city_2.number_of_visits = 2
    fake_city_2.first_visit_date = date(2022, 1, 1)
    fake_city_2.last_visit_date = date(2023, 1, 1)
    fake_city_2.has_souvenir = True
    fake_city_2.average_rating = 4.0

    # Настраиваем возвращаемые значения моков
    mock_get_all_visited_cities.return_value = [fake_city_1, fake_city_2]
    mock_apply_sort.return_value = [fake_city_1, fake_city_2]

    # Выполняем тестируемый код
    report = CityReport(1).get_report()

    # Проверка результата
    assert report == [
        (
            'Город',
            'Регион',
            'Количество посещений',
            'Дата первого посещения',
            'Дата последнего посещения',
            'Наличие сувенира',
            'Средняя оценка',
        ),
        ('Город 1', 'Регион 1 область', 1, '2024-01-01', '2024-01-01', '-', 3.0),
        ('Город 2', 'Регион 1 область', 2, '2022-01-01', '2023-01-01', '+', 4.0),
    ]

    mock_get_all_visited_cities.assert_called_once_with(1)
    mock_apply_sort.assert_called_once_with([fake_city_1, fake_city_2], 'last_visit_date_down')


def test__city_report__no_visited_cities(mocker):
    # Мокаем функцию, получающую все посещённые города
    mock_get_visited_cities = mocker.patch('account.report.get_all_visited_cities')

    # Мокаем QuerySet как пустой список, чтобы симулировать отсутствие данных
    empty_queryset = mocker.MagicMock()

    # Настройка возвращаемого значения: пустой QuerySet
    mock_get_visited_cities.return_value = empty_queryset

    # Мокаем метод order_by для пустого QuerySet, он должен вернуть сам себя
    empty_queryset.order_by.return_value = empty_queryset

    # Выполнение отчёта
    report = CityReport(1).get_report()

    # Ожидаем, что отчёт будет содержать только заголовки
    assert report == [
        (
            'Город',
            'Регион',
            'Количество посещений',
            'Дата первого посещения',
            'Дата последнего посещения',
            'Наличие сувенира',
            'Средняя оценка',
        ),
    ]

    # Проверяем, что функция для получения городов была вызвана один раз с параметром 1
    mock_get_visited_cities.assert_called_once_with(1)


@pytest.mark.django_db
def test__region_report(mocker):
    # Мокаем функцию, получающую регионы
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    # Создаём фейковый регион
    fake_region = mocker.MagicMock()
    fake_region.__str__.return_value = 'Регион 1 область'
    fake_region.num_total = 2
    fake_region.num_visited = 2

    # Настройка возвращаемого значения
    mock_get_regions.return_value = [fake_region]

    # Выполняем отчёт
    report = RegionReport(1).get_report()

    # Проверка содержимого отчёта
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


def test__region_report__empty_regions(mocker):
    # Мокаем функцию, получающую регионы
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    # Настройка возвращаемого значения: пустой список
    mock_get_regions.return_value = []

    # Выполнение отчёта
    report = RegionReport(1).get_report()

    # Ожидаем, что отчёт будет содержать только заголовки
    assert report == [
        (
            'Регион',
            'Всего городов',
            'Посещено городов, шт',
            'Посещено городов, %',
            'Осталось посетить, шт',
        ),
    ]

    mock_get_regions.assert_called_once_with(1)


def test__region_report__no_visited_cities(mocker):
    # Мокаем функцию, получающую регионы
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    # Фейковый регион с 2 городами, но без посещённых
    fake_region = mocker.MagicMock()
    fake_region.__str__.return_value = 'Регион 2 область'
    fake_region.num_total = 2
    fake_region.num_visited = 0

    # Настройка возвращаемого значения
    mock_get_regions.return_value = [fake_region]

    # Выполнение отчёта
    report = RegionReport(1).get_report()

    # Проверка содержимого отчёта
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

    mock_get_regions.assert_called_once_with(1)


def test__region_report__division_by_zero_1(mocker):
    # Мокаем функцию, получающую регионы
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    # Фейковый регион с 0 посещёнными городами
    fake_region = mocker.MagicMock()
    fake_region.__str__.return_value = 'Регион 3 область'
    fake_region.num_total = 3
    fake_region.num_visited = 0

    # Настройка возвращаемого значения
    mock_get_regions.return_value = [fake_region]

    # Выполнение отчёта
    report = RegionReport(1).get_report()

    # Проверка содержимого отчёта
    assert report == [
        (
            'Регион',
            'Всего городов',
            'Посещено городов, шт',
            'Посещено городов, %',
            'Осталось посетить, шт',
        ),
        ('Регион 3 область', 3, 0, '0%', 3),
    ]

    mock_get_regions.assert_called_once_with(1)


def test__region_report__division_by_zero_2(mocker):
    # Мокаем функцию, получающую регионы
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    # Фейковый регион с 0 посещёнными городами
    fake_region = mocker.MagicMock()
    fake_region.__str__.return_value = 'Регион 3 область'
    fake_region.num_total = 0
    fake_region.num_visited = 0

    # Настройка возвращаемого значения
    mock_get_regions.return_value = [fake_region]

    # Выполнение отчёта
    report = RegionReport(1).get_report()

    # Проверка содержимого отчёта
    assert report == [
        (
            'Регион',
            'Всего городов',
            'Посещено городов, шт',
            'Посещено городов, %',
            'Осталось посетить, шт',
        ),
        ('Регион 3 область', 0, 0, '0%', 0),
    ]

    mock_get_regions.assert_called_once_with(1)


def test__region_report__multiple_regions(mocker):
    # Мокаем функцию, получающую регионы
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    # Фейковые регионы с разным количеством посещённых городов
    fake_region_1 = mocker.MagicMock()
    fake_region_1.__str__.return_value = 'Регион 1 область'
    fake_region_1.num_total = 2
    fake_region_1.num_visited = 2

    fake_region_2 = mocker.MagicMock()
    fake_region_2.__str__.return_value = 'Регион 2 область'
    fake_region_2.num_total = 3
    fake_region_2.num_visited = 1

    mock_get_regions.return_value = [fake_region_1, fake_region_2]

    # Выполнение отчёта
    report = RegionReport(1).get_report()

    # Проверка содержимого отчёта
    assert report == [
        (
            'Регион',
            'Всего городов',
            'Посещено городов, шт',
            'Посещено городов, %',
            'Осталось посетить, шт',
        ),
        ('Регион 1 область', 2, 2, '100%', 0),
        ('Регион 2 область', 3, 1, '33%', 2),
    ]

    mock_get_regions.assert_called_once_with(1)


def test__region_report__percentage_rounding(mocker):
    # Мокаем функцию, получающую регионы
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    # Фейковый регион с 2 городами, 1 из которых посещён
    fake_region = mocker.MagicMock()
    fake_region.__str__.return_value = 'Регион 4 область'
    fake_region.num_total = 2
    fake_region.num_visited = 1

    # Настройка возвращаемого значения
    mock_get_regions.return_value = [fake_region]

    # Выполнение отчёта
    report = RegionReport(1).get_report()

    # Проверка содержимого отчёта
    assert report == [
        (
            'Регион',
            'Всего городов',
            'Посещено городов, шт',
            'Посещено городов, %',
            'Осталось посетить, шт',
        ),
        ('Регион 4 область', 2, 1, '50%', 1),
    ]

    mock_get_regions.assert_called_once_with(1)


def test__region_report__sorting_by_visited_cities(mocker):
    # Мокаем функцию, получающую регионы
    mock_get_regions = mocker.patch('account.report.get_all_region_with_visited_cities')

    # Фейковые регионы с разным количеством посещённых городов
    fake_region_1 = mocker.MagicMock()
    fake_region_1.__str__.return_value = 'Регион 1 область'
    fake_region_1.num_total = 3
    fake_region_1.num_visited = 3

    fake_region_2 = mocker.MagicMock()
    fake_region_2.__str__.return_value = 'Регион 2 область'
    fake_region_2.num_total = 2
    fake_region_2.num_visited = 1

    mock_get_regions.return_value = [fake_region_1, fake_region_2]

    # Выполнение отчёта
    report = RegionReport(1).get_report()

    # Проверка содержимого отчёта
    assert report[1] == ('Регион 1 область', 3, 3, '100%', 0)
    assert report[2] == ('Регион 2 область', 2, 1, '50%', 1)

    mock_get_regions.assert_called_once_with(1)


@pytest.mark.django_db
def test__area_report(mocker):
    # Мокаем функцию, получающую округа
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    # Создаём фейковый объект федерального округа
    fake_area = mocker.MagicMock()
    fake_area.title = 'Округ 1'
    fake_area.total_regions = 1
    fake_area.visited_regions = 1

    # Настройка возвращаемого значения
    mock_get_areas.return_value = [fake_area]

    # Выполнение метода
    report = AreaReport(1).get_report()

    # Проверка содержимого отчёта
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

    mock_get_areas.assert_called_once_with(1)


def test__area_report__empty_area(mocker):
    # Мокаем функцию, получающую округа
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    # Настройка возвращаемого значения: пустой список
    mock_get_areas.return_value = []

    # Выполнение метода
    report = AreaReport(1).get_report()

    # Ожидаем, что отчёт будет содержать только заголовки
    assert report == [
        (
            'Федеральный округ',
            'Всего регионов, шт',
            'Посещено регионов, шт',
            'Посещено регионов, %',
            'Осталось посетить, шт',
        ),
    ]

    mock_get_areas.assert_called_once_with(1)


def test__area_report__no_visited_regions(mocker):
    # Мокаем функцию, получающую округа
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    # Фейковый округ с 2 регионами, но без посещённых
    fake_area = mocker.MagicMock()
    fake_area.title = 'Округ 2'
    fake_area.total_regions = 2
    fake_area.visited_regions = 0

    # Настройка возвращаемого значения
    mock_get_areas.return_value = [fake_area]

    # Выполнение метода
    report = AreaReport(1).get_report()

    # Проверка содержания отчёта
    assert report == [
        (
            'Федеральный округ',
            'Всего регионов, шт',
            'Посещено регионов, шт',
            'Посещено регионов, %',
            'Осталось посетить, шт',
        ),
        ('Округ 2', 2, 0, '0%', 2),
    ]

    mock_get_areas.assert_called_once_with(1)


def test__area_report__zero_visited_regions(mocker):
    # Мокаем функцию, получающую округа
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    # Фейковый округ с 0 регионами, чтобы избежать деления на ноль
    fake_area = mocker.MagicMock()
    fake_area.title = 'Округ 3'
    fake_area.total_regions = 0
    fake_area.visited_regions = 0

    # Настройка возвращаемого значения
    mock_get_areas.return_value = [fake_area]

    # Выполнение метода
    report = AreaReport(1).get_report()

    # Проверка содержания отчёта
    assert report == [
        (
            'Федеральный округ',
            'Всего регионов, шт',
            'Посещено регионов, шт',
            'Посещено регионов, %',
            'Осталось посетить, шт',
        ),
        ('Округ 3', 0, 0, '0%', 0),
    ]

    mock_get_areas.assert_called_once_with(1)


def test__area_report__rounding_percentage(mocker):
    # Мокаем функцию, получающую округа
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    # Фейковый округ с 3 регионами, 2 из которых посещены
    fake_area = mocker.MagicMock()
    fake_area.title = 'Округ 4'
    fake_area.total_regions = 3
    fake_area.visited_regions = 2

    # Настройка возвращаемого значения
    mock_get_areas.return_value = [fake_area]

    # Выполнение метода
    report = AreaReport(1).get_report()

    # Проверка содержания отчёта с округлением
    assert report == [
        (
            'Федеральный округ',
            'Всего регионов, шт',
            'Посещено регионов, шт',
            'Посещено регионов, %',
            'Осталось посетить, шт',
        ),
        ('Округ 4', 3, 2, '67%', 1),
    ]

    mock_get_areas.assert_called_once_with(1)


def test__area_report__sorting_by_percentage(mocker):
    # Мокаем функцию, получающую округа
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    # Фейковые округа с разными процентами посещённых регионов
    fake_area_1 = mocker.MagicMock()
    fake_area_1.title = 'Округ 1'
    fake_area_1.total_regions = 2
    fake_area_1.visited_regions = 1

    fake_area_2 = mocker.MagicMock()
    fake_area_2.title = 'Округ 2'
    fake_area_2.total_regions = 2
    fake_area_2.visited_regions = 0

    mock_get_areas.return_value = [fake_area_1, fake_area_2]

    # Выполнение метода
    report = AreaReport(1).get_report()

    # Проверка содержания отчёта: Округ 1 должен быть первым
    assert report[1] == ('Округ 1', 2, 1, '50%', 1)
    assert report[2] == ('Округ 2', 2, 0, '0%', 2)

    mock_get_areas.assert_called_once_with(1)


def test__area_report__external_calls(mocker):
    # Мокаем функцию, получающую округа
    mock_get_areas = mocker.patch('account.report.get_visited_areas')

    # Настройка возвращаемого значения
    mock_get_areas.return_value = []

    # Выполнение метода
    AreaReport(1).get_report()

    # Проверка, что функция get_visited_areas была вызвана с правильным user_id
    mock_get_areas.assert_called_once_with(1)
