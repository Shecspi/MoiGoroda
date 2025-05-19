"""
Этот модуль содержит тесты для следующих функций репозитория приложения Region:
 - get_all_regions
 - get_all_cities_in_region
 - get_all_region_with_visited_cities

Для мока зависимостей использованы средства `pytest-mock`, что позволяет контролировать поведение внешних зависимостей
и тестировать логику работы с QuerySet и базой данных без необходимости реального обращения к базе данных.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from region.services.db import (
    get_all_regions,
    get_all_region_with_visited_cities,
    get_all_cities_in_region,
)


###################
# get_all_regions #
###################


def test_get_all_regions_calls_correct_queryset_methods(mocker):
    mock_region = mocker.patch('region.services.db.Region')
    mock_qs = mocker.MagicMock(name='QuerySet')

    mock_region.objects.select_related.return_value = mock_qs
    mock_qs.annotate.return_value = mock_qs
    mock_qs.order_by.return_value = mock_qs

    result = get_all_regions()

    mock_region.objects.select_related.assert_called_once_with('area')
    mock_qs.annotate.assert_called_once()
    mock_qs.order_by.assert_called_once_with('title')
    assert result == mock_qs.order_by.return_value


def test_get_all_regions_uses_correct_annotation(mocker):
    mock_count = mocker.patch('region.services.db.Count')
    mock_region = mocker.patch('region.services.db.Region')
    mock_qs = mocker.MagicMock(name='QuerySet')

    mock_region.objects.select_related.return_value = mock_qs
    mock_qs.annotate.return_value = mock_qs
    mock_qs.order_by.return_value = mock_qs

    get_all_regions()

    mock_count.assert_called_once_with('city', distinct=True)
    mock_qs.annotate.assert_called_once_with(num_total=mock_count.return_value)


######################################
# get_all_region_with_visited_cities #
######################################


def test_get_all_region_with_visited_cities_calls_correct_queryset_methods(mocker):
    # Мокаем Count, Q и Region
    mocker.patch('region.services.db.Count')
    mocker.patch('region.services.db.Q')
    mock_region = mocker.patch('region.services.db.Region')

    # Создаём мок QuerySet
    mock_qs = mocker.MagicMock(name='QuerySet')

    # Патчим методы
    mock_region.objects.select_related.return_value = mock_qs
    mock_qs.annotate.return_value = mock_qs
    mock_qs.order_by.return_value = mock_qs

    user_id = 42
    result = get_all_region_with_visited_cities(user_id)

    # Проверяем, что select_related был вызван с правильным аргументом
    mock_region.objects.select_related.assert_called_once_with('area')
    mock_qs.annotate.assert_called_once()
    mock_qs.order_by.assert_called_once_with('-num_visited', 'title')

    # Проверяем, что результат — тот же объект, что возвращается после всех вызовов
    assert result == mock_qs.order_by.return_value


def test_get_all_region_with_visited_cities_uses_correct_annotations(mocker):
    # Мокаем Count, Q и Region
    mock_count = mocker.patch('region.services.db.Count')
    mock_q = mocker.patch('region.services.db.Q')
    mock_region = mocker.patch('region.services.db.Region')

    # Создаём мок QuerySet
    mock_qs = mocker.MagicMock(name='QuerySet')

    # Патчим методы
    mock_region.objects.select_related.return_value = mock_qs
    mock_qs.annotate.return_value = mock_qs
    mock_qs.order_by.return_value = mock_qs

    user_id = 101
    get_all_region_with_visited_cities(user_id)

    # Проверяем, что Q был вызван с правильным фильтром
    mock_q.assert_called_once_with(city__visitedcity__user_id=user_id)

    # Проверяем, что Count был вызван с нужными аргументами
    mock_count.assert_any_call('city', distinct=True)
    mock_count.assert_any_call('city', filter=mock_q.return_value, distinct=True)

    # Проверяем, что annotate был вызван с правильными аннотациями
    mock_qs.annotate.assert_called_once_with(
        num_total=mock_count.return_value,
        num_visited=mock_count.return_value,
    )


############################
# get_all_cities_in_region #
############################


def test_get_all_cities_in_region_with_mocker(mocker):
    # Мокаем все используемые в функции зависимости
    mock_city = mocker.patch('region.services.db.City')
    mock_exists = mocker.patch('region.services.db.Exists')
    mock_subquery = mocker.patch('region.services.db.Subquery')
    mock_coalesce = mocker.patch('region.services.db.Coalesce')
    mock_min = mocker.patch('region.services.db.Min')
    mock_max = mocker.patch('region.services.db.Max')
    mocker.patch('region.services.db.VisitedCity')
    mocker.patch('region.services.db.Q')
    mocker.patch('region.services.db.Count')
    mocker.patch('region.services.db.Avg')
    mocker.patch('region.services.db.ArrayAgg')
    mocker.patch('region.services.db.Value')
    mocker.patch('region.services.db.ArrayField')
    mocker.patch('region.services.db.IntegerField')
    mocker.patch('region.services.db.DateField')

    mock_queryset = mocker.MagicMock(name='CityQuerySet')
    mock_city.objects.filter.return_value = mock_queryset

    first_annotate = mocker.MagicMock(name='FirstAnnotate')
    second_annotate = mocker.MagicMock(name='SecondAnnotate')
    mock_queryset.annotate.return_value = first_annotate
    first_annotate.annotate.return_value = second_annotate

    user = mocker.Mock()
    region_id = 42

    result = get_all_cities_in_region(user=user, region_id=region_id)

    assert mock_city.objects.filter.call_args.args == (), 'filter called with wrong positional args'
    assert mock_city.objects.filter.call_args.kwargs == {'region_id': region_id}
    assert mock_queryset.annotate.call_count == 1
    assert first_annotate.annotate.call_count == 1
    assert result == second_annotate

    # Проверка аргументов первого annotate
    mock_queryset.annotate.assert_called_once_with(
        visit_dates=mock_coalesce.return_value,
        first_visit_date=mock_min.return_value,
        last_visit_date=mock_max.return_value,
        number_of_visits=mock_subquery.return_value,
        is_visited=mock_exists.return_value,
        has_magnet=mock_exists.return_value,
    )

    # Проверка аргументов второго annotate
    first_annotate.annotate.assert_called_once_with(
        visited_id=mock_subquery.return_value,
        rating=mock_subquery.return_value,
    )
