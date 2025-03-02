"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import QuerySet, Q, Min, Max

from services.db.selected_region.filter import (
    filter_has_magnet,
    filter_has_no_magnet,
    filter_current_year,
    ArrayLength,
    filter_last_year,
    apply_filter_to_queryset,
    FILTER_FUNCTIONS,
)


def test__filter_has_magnet_correctly_filters_queryset(mocker):
    # Создаём мок-объект для queryset и user
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_user = mocker.Mock(spec=AbstractBaseUser)

    # Мокируем метод filter
    mock_filter = mocker.patch.object(mock_queryset, 'filter')

    # Запускаем функцию
    result = filter_has_magnet(mock_queryset, mock_user)

    # Проверяем, что filter был вызван с правильными параметрами и возвращает правильный результат
    mock_filter.assert_called_once_with(has_magnet=True, is_visited=True)
    assert result == mock_queryset.filter.return_value


def test__filter_has_magnet_does_not_use_user(mocker):
    """
    Проверяет, что параметр `user` не используется при фильтрации.
    """
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_user = mocker.Mock(spec=AbstractBaseUser)

    filter_has_magnet(mock_queryset, mock_user)

    # Проверяем, что методы пользователя не вызывались
    mock_user.assert_not_called()


def test__filter_has_no_magnet_correctly_filters_queryset(mocker):
    # Создаём мок-объект для queryset и user
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_user = mocker.Mock(spec=AbstractBaseUser)

    # Мокируем метод filter
    mock_filter = mocker.patch.object(mock_queryset, 'filter')

    # Запускаем функцию
    result = filter_has_no_magnet(mock_queryset, mock_user)

    # Проверяем, что filter был вызван с правильными параметрами и возвращает правильный результат
    mock_filter.assert_called_once_with(has_magnet=False, is_visited=True)
    assert result == mock_queryset.filter.return_value


def test__filter_has_no_magnet_does_not_use_user(mocker):
    """
    Проверяет, что параметр `user` не используется при фильтрации.
    """
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_user = mocker.Mock(spec=AbstractBaseUser)

    filter_has_no_magnet(mock_queryset, mock_user)

    # Проверяем, что методы пользователя не вызывались
    mock_user.assert_not_called()


def test__filter_current_year(mocker):
    """
    Проверяет корректность построения QuerySet для фильтрации городов текущего года.

    Тест убеждается, что:
    1. Аннотации visit_dates, first_visit_date и last_visit_date используют:
       - Фильтр по текущему году и переданному пользователю
       - Правильные агрегационные функции (ArrayAgg, Min, Max)
       - Параметры distinct и ordering для visit_dates
    2. Исключаются города с пустыми visit_dates
    3. Добавляется аннотация number_of_visits через ArrayLength
    4. Цепочка вызовов сохраняется: annotate → exclude → annotate

    Тест не требует подключения к БД - проверяется только структура запроса.
    """

    # Мокаем datetime.today().year, чтобы контролировать текущий год
    mock_datetime = mocker.patch('services.db.selected_region.filter.datetime')
    mock_datetime.today.return_value.year = 2025

    # Создаем мок QuerySet и пользователя
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_user = mocker.Mock(spec=AbstractBaseUser)
    mock_user.id = 1  # Добавляем ID для проверки в фильтрах

    # Вызываем тестируемую функцию
    result = filter_current_year(mock_queryset, mock_user)

    # Проверяем цепочку вызовов
    expected_filter = Q(visitedcity__user=mock_user, visitedcity__date_of_visit__year=2025)

    # Проверяем аннотации
    mock_queryset.annotate.assert_called_once_with(
        visit_dates=ArrayAgg(
            'visitedcity__date_of_visit',
            filter=expected_filter,
            distinct=True,
            ordering='visitedcity__date_of_visit',
        ),
        first_visit_date=Min('visitedcity__date_of_visit', filter=expected_filter),
        last_visit_date=Max('visitedcity__date_of_visit', filter=expected_filter),
    )

    # Проверяем exclude и вторую аннотацию
    annotated_queryset = mock_queryset.annotate.return_value
    annotated_queryset.exclude.assert_called_once_with(Q(visit_dates=[]))

    excluded_queryset = annotated_queryset.exclude.return_value
    excluded_queryset.annotate.assert_called_once_with(number_of_visits=ArrayLength('visit_dates'))

    # Проверяем возвращаемый результат
    assert result == excluded_queryset.annotate.return_value


def test__current_year_logic(mocker):
    """
    Проверяет динамическое использование текущего года в фильтрах.

    Ключевые проверки:
    1. Фильтры во всех аннотациях используют актуальный год
    2. При изменении системного времени:
       - В фильтрах автоматически меняется год
       - Не требуется ручное обновление параметров теста

    Тест мокает системное время для проверки временнóй логики.
    Пример: если текущий год 2025, фильтр должен использовать 2025 год,
    а при смене времени на 2026 - автоматически обновиться.
    """

    # Проверяем что используется текущий год
    mock_datetime = mocker.patch('services.db.selected_region.filter.datetime')
    mock_datetime.today.return_value.year = 2026  # Меняем год

    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_user = mocker.Mock(spec=AbstractBaseUser)

    filter_current_year(mock_queryset, mock_user)

    # Проверяем что фильтр использует 2026 год
    expected_filter = Q(visitedcity__user=mock_user, visitedcity__date_of_visit__year=2026)
    mock_queryset.annotate.assert_called_once()
    call_args = mock_queryset.annotate.call_args.kwargs
    assert call_args['visit_dates'].filter == expected_filter


def test__filter_last_year(mocker):
    """
    Проверяет корректность построения QuerySet для фильтрации городов прошлого года.

    Тест убеждается, что:
    1. Аннотации visit_dates, first_visit_date и last_visit_date используют:
       - Фильтр по предыдущему году и переданному пользователю
       - Правильные агрегационные функции (ArrayAgg, Min, Max)
       - Параметры distinct и ordering для visit_dates
    2. Исключаются города с пустыми visit_dates
    3. Добавляется аннотация number_of_visits через ArrayLength
    4. Цепочка вызовов сохраняется: annotate → exclude → annotate

    Тест проверяет структуру запроса без подключения к БД.
    """
    # Мокаем datetime для контроля года
    mock_datetime = mocker.patch('services.db.selected_region.filter.datetime')
    mock_datetime.today.return_value.year = 2023  # Текущий год для теста

    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_user = mocker.Mock(spec=AbstractBaseUser)
    mock_user.id = 1

    filter_last_year(mock_queryset, mock_user)

    # Ожидаемый предыдущий год = 2023 - 1 = 2022
    expected_filter = Q(visitedcity__user=mock_user, visitedcity__date_of_visit__year=2022)

    # Проверка аннотаций
    annotate_call = mock_queryset.annotate.call_args
    assert annotate_call.kwargs['visit_dates'].filter == expected_filter
    assert annotate_call.kwargs['first_visit_date'].filter == expected_filter
    assert annotate_call.kwargs['last_visit_date'].filter == expected_filter

    # Проверка цепочки вызовов
    annotated_queryset = mock_queryset.annotate.return_value
    annotated_queryset.exclude.assert_called_once_with(Q(visit_dates=[]))
    annotated_queryset.exclude.return_value.annotate.assert_called_once_with(
        number_of_visits=ArrayLength('visit_dates')
    )


def test__last_year_logic(mocker):
    """
    Проверяет динамическое вычисление предыдущего года в фильтрах.

    Ключевые проверки:
    1. Фильтры используют year = (current_year - 1)
    2. При изменении системного времени:
       - Предыдущий год автоматически пересчитывается
       - Фильтры всегда отстают на 1 год от текущего
    """
    # Настраиваем мок QuerySet с поддержкой цепочки вызовов
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_queryset.annotate.return_value = (
        mock_queryset  # Для цепочки annotate().exclude().annotate()
    )

    # Мокаем datetime
    mock_datetime = mocker.patch('services.db.selected_region.filter.datetime')

    # Тест кейс 1: текущий 2024 → предыдущий 2023
    mock_datetime.today.return_value.year = 2024
    filter_last_year(mock_queryset, mocker.Mock(spec=AbstractBaseUser))

    # Проверяем фильтр для 2023
    expected_filter_2023 = Q(visitedcity__user=mocker.ANY, visitedcity__date_of_visit__year=2023)
    mock_queryset.annotate.assert_called_once()
    call_kwargs = mock_queryset.annotate.call_args.kwargs
    assert call_kwargs['visit_dates'].filter == expected_filter_2023

    # Сбрасываем мок для следующего кейса
    mock_queryset.reset_mock()

    # Тест кейс 2: текущий 2025 → предыдущий 2024
    mock_datetime.today.return_value.year = 2025
    filter_last_year(mock_queryset, mocker.Mock(spec=AbstractBaseUser))

    # Проверяем фильтр для 2024
    expected_filter_2024 = Q(visitedcity__user=mocker.ANY, visitedcity__date_of_visit__year=2024)
    mock_queryset.annotate.assert_called_once()
    call_kwargs = mock_queryset.annotate.call_args.kwargs
    assert call_kwargs['visit_dates'].filter == expected_filter_2024


def test__apply_filter_calls_correct_function(mocker):
    """
    Проверяет вызов правильной функции фильтрации через apply_filter_to_queryset
    """
    mock_filter = mocker.Mock(return_value=QuerySet())
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_user = mocker.Mock(spec=AbstractBaseUser)

    # Подменяем словарь фильтров
    mocker.patch.dict(
        'services.db.selected_region.filter.FILTER_FUNCTIONS',
        {'test_filter': mock_filter},
        clear=False,
    )

    result = apply_filter_to_queryset(mock_queryset, mock_user, 'test_filter')

    mock_filter.assert_called_once_with(mock_queryset, mock_user)
    assert result == mock_filter.return_value


def test__apply_filter_raises_error_for_unknown_filter(mocker):
    """
    Проверяет вызов исключения для неизвестного фильтра
    """
    mock_filter = mocker.Mock(return_value=QuerySet())
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_user = mocker.Mock(spec=AbstractBaseUser)

    with pytest.raises(KeyError) as exc:
        apply_filter_to_queryset(mock_queryset, mock_user, 'invalid_filter')

    assert 'Неизвестный фильтр: invalid_filter' in str(exc.value)


@pytest.mark.parametrize('filter_name', FILTER_FUNCTIONS.keys())
def test__all_registered_filters_are_called(mocker, filter_name):
    """
    Параметризованный тест для всех зарегистрированных фильтров
    """
    mock_filter = mocker.Mock(return_value=QuerySet())
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_user = mocker.Mock(spec=AbstractBaseUser)
    mocker.patch.dict(
        'services.db.selected_region.filter.FILTER_FUNCTIONS',
        {filter_name: mock_filter},
        clear=False,
    )

    apply_filter_to_queryset(mock_queryset, mock_user, filter_name)

    mock_filter.assert_called_once()
