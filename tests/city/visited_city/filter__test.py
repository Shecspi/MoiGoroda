"""
Тесты для модуля filter.py
"""

import pytest
from unittest.mock import Mock
from django.db.models import QuerySet, Q, OuterRef

from city.models import VisitedCity
from services.db.visited_city.filter import (
    filter_has_magnet,
    filter_has_no_magnet,
    filter_last_year,
    apply_filter_to_queryset,
    FILTER_FUNCTIONS,
    filter_current_year,
    filter_by_year,
)


def test__filter_has_magnet_correctly_filters_queryset(mocker):
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_filter = mocker.patch.object(mock_queryset, 'filter')

    result = filter_has_magnet(mock_queryset, user_id=1)

    mock_filter.assert_called_once_with(has_souvenir=True)
    assert result == mock_queryset.filter.return_value


def test__filter_has_magnet_does_not_use_user_id(mocker):
    """
    Проверяет, что параметр `user` не используется при фильтрации.
    Функция filter_has_magnet ожидает `user` для унификации интерфейса, но не должна его использовать.
    """
    mock_queryset = mocker.Mock(spec=QuerySet)
    filter_has_magnet(mock_queryset, user_id=1)
    # Проверяем, что user_id не используется в запросе (кроме подзапросов)
    mock_queryset.filter.assert_called_once_with(has_souvenir=True)


def test__filter_has_no_magnet_correctly_filters_queryset(mocker):
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_filter = mocker.patch.object(mock_queryset, 'filter')

    result = filter_has_no_magnet(mock_queryset, user_id=1)

    mock_filter.assert_called_once_with(has_magnet=False)
    assert result == mock_queryset.filter.return_value


def test__filter_has_no_magnet_does_not_use_user_id(mocker):
    """
    Проверяет, что параметр `user` не используется при фильтрации.
    Функция filter_has_magnet ожидает `user` для унификации интерфейса, но не должна его использовать.
    """
    mock_queryset = mocker.Mock(spec=QuerySet)
    filter_has_no_magnet(mock_queryset, user_id=1)
    mock_queryset.filter.assert_called_once_with(has_magnet=False)


def test__filter_current_yetest__filter_current_year_calls_filter_by_year_with_correct_argsar_calls_filter_by_year_with_correct_args(
    mocker,
):
    # Мокаем datetime.date.today() в целевом модуле
    mock_date = mocker.patch('services.db.visited_city.filter.date')
    mock_date.today.return_value.year = 2023

    # Замокаем функцию filter_by_year
    mock_filter_by_year = mocker.patch(
        'services.db.visited_city.filter.filter_by_year', return_value=mocker.Mock(spec=QuerySet)
    )

    mock_queryset = mocker.Mock(spec=QuerySet)
    user_id = 1

    # Вызываем тестируемую функцию
    filter_current_year(mock_queryset, user_id)

    # Проверяем вызов filter_by_year с правильными аргументами
    mock_filter_by_year.assert_called_once_with(mock_queryset, user_id, 2023)


def test__filter_by_year_annotations(mocker):
    # Мокаем объекты, связанные с ORM
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_annotated_queryset = mocker.Mock()
    mock_excluded_queryset = mocker.Mock()

    # Настраиваем цепочку вызовов
    mock_queryset.annotate.return_value = mock_annotated_queryset
    mock_annotated_queryset.exclude.return_value = mock_excluded_queryset
    mock_excluded_queryset.annotate.return_value = 'final_queryset'

    # Мокаем Subquery
    mock_subquery = mocker.Mock()
    mocker.patch('services.db.visited_city.filter.Subquery', return_value=mock_subquery)

    # Мокаем VisitedCity.objects.filter и связанные методы
    mock_filter = mocker.Mock()
    mocker.patch.object(VisitedCity.objects, 'filter', return_value=mock_filter)
    mock_filter.values.return_value = mock_filter  # Поддерживаем цепочку values()
    mock_filter.annotate.return_value = mock_filter  # Поддерживаем цепочку annotate()

    user_id = 1
    year = 2023

    # Вызываем тестируемую функцию
    result = filter_by_year(mock_queryset, user_id, year)

    # Проверяем последовательность вызовов в QuerySet
    mock_queryset.annotate.assert_called_once_with(
        visit_dates=mock_subquery, first_visit_date=mock_subquery, last_visit_date=mock_subquery
    )
    mock_annotated_queryset.exclude.assert_called_once_with(Q(visit_dates=[]))
    mock_excluded_queryset.annotate.assert_called_once_with(number_of_visits=mock_subquery)

    # Проверяем вызовы фильтрации в подзапросах
    VisitedCity.objects.filter.assert_any_call(
        user_id=user_id, city_id=OuterRef('city_id'), date_of_visit__year=year
    )


# Не работает
def test__filter_last_year_calls_filter_by_year_with_correct_args(mocker):
    # Мокаем datetime.date.today()
    mock_date = mocker.patch("services.db.visited_city.filter.date")
    mock_date.today.return_value.year = 2023  # Текущий год

    # Замокаем filter_by_year и её возвращаемое значение
    mock_filter_by_year = mocker.patch(
        "services.db.visited_city.filter.filter_by_year",
        return_value=mocker.Mock(spec=QuerySet)
    )

    mock_queryset = mocker.Mock(spec=QuerySet)
    user_id = 1

    # Вызываем тестируемую функцию
    filter_last_year(mock_queryset, user_id)

    # Проверяем, что filter_by_year вызвана с year=2022
    mock_filter_by_year.assert_called_once_with(mock_


# Не работает
def test__filter_by_year_annotations_and_subqueries(mocker):
    # Мокаем Subquery и другие методы
    mock_queryset = mocker.Mock(spec=QuerySet)
    user_id = 1
    year = 2023

    # Замокаем вызовы annotate и exclude
    annotated_queryset = Mock()
    mock_queryset.annotate.return_value = annotated_queryset
    annotated_queryset.exclude.return_value.annotate.return_value = 'final_queryset'

    from services.db.filter import filter_by_year

    result = filter_by_year(mock_queryset, user_id, year)

    # Проверяем наличие подзапросов в аннотациях
    annotate_calls = mock_queryset.annotate.call_args_list
    assert any('visit_dates' in call.kwargs for call in annotate_calls)
    assert any('first_visit_date' in call.kwargs for call in annotate_calls)
    assert any('last_visit_date' in call.kwargs for call in annotate_calls)

    # Проверяем исключение пустых visit_dates
    annotated_queryset.exclude.assert_called_once_with(Q(visit_dates=[]))

    # Проверяем аннотацию number_of_visits
    annotated_queryset.exclude.return_value.annotate.assert_called_once()


def test__apply_filter_calls_correct_function(mocker):
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_filter = mocker.Mock(return_value=mock_queryset)
    mocker.patch.dict(FILTER_FUNCTIONS, {'test_filter': mock_filter})

    result = apply_filter_to_queryset(mock_queryset, user_id=1, filter_name='test_filter')

    mock_filter.assert_called_once_with(mock_queryset, 1)
    assert result == mock_queryset


def test__apply_filter_raises_error_for_unknown_filter():
    with pytest.raises(KeyError) as exc:
        apply_filter_to_queryset(QuerySet(), user_id=1, filter_name='unknown')
    assert 'Неизвестный фильтр: unknown' in str(exc.value)


@pytest.mark.parametrize('filter_name', FILTER_FUNCTIONS.keys())
def test__all_registered_filters_are_called(mocker, filter_name):
    mock_filter = mocker.Mock(return_value=QuerySet())
    mocker.patch.dict(FILTER_FUNCTIONS, {filter_name: mock_filter})

    apply_filter_to_queryset(QuerySet(), user_id=1, filter_name=filter_name)
    mock_filter.assert_called_once()
