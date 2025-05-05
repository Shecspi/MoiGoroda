"""
Тесты для модуля сортировки visited_city/sort.py
"""

import pytest
from django.db.models import QuerySet

from city.sort import SORT_FUNCTIONS, apply_sort_to_queryset


@pytest.mark.parametrize('sort_name', SORT_FUNCTIONS.keys())
def test__apply_sort_to_queryset_calls_correct_function(mocker, sort_name):
    """
    Проверяет, что apply_sort_to_queryset вызывает соответствующую функцию из SORT_FUNCTIONS.
    """
    mock_queryset = mocker.Mock(spec=QuerySet)
    mock_func = mocker.Mock(return_value='sorted_queryset')
    mocker.patch.dict('city.sort.SORT_FUNCTIONS', {sort_name: mock_func})

    result = apply_sort_to_queryset(mock_queryset, sort_name)

    mock_func.assert_called_once_with(mock_queryset)
    assert result == 'sorted_queryset'


def test__apply_sort_to_queryset_raises_for_unknown_sort(mocker):
    """
    Проверяет, что при неизвестном параметре сортировки вызывается KeyError.
    """
    mock_queryset = mocker.Mock(spec=QuerySet)

    with pytest.raises(KeyError) as exc_info:
        apply_sort_to_queryset(mock_queryset, 'invalid_sort')

    assert 'Неизвестный параметр сортировки' in str(exc_info.value)


@pytest.mark.parametrize(
    'sort_name, expected_order_by_args',
    [
        ('name_up', ('city__title',)),
        ('name_down', ('-city__title',)),
    ],
)
def test__name_sorts_call_order_by_correctly(mocker, sort_name, expected_order_by_args):
    """
    Проверяет, что сортировка по имени вызывает order_by с корректными аргументами.
    """
    mock_queryset = mocker.Mock(spec=QuerySet)
    result = apply_sort_to_queryset(mock_queryset, sort_name)

    mock_queryset.order_by.assert_called_once_with(*expected_order_by_args)
    assert result == mock_queryset.order_by.return_value


@pytest.mark.parametrize(
    'sort_name, field_name, direction',
    [
        ('first_visit_date_up', 'first_visit_date', 'asc'),
        ('first_visit_date_down', 'first_visit_date', 'desc'),
        ('last_visit_date_up', 'last_visit_date', 'asc'),
        ('last_visit_date_down', 'last_visit_date', 'desc'),
        ('number_of_visits_up', 'number_of_visits', 'asc'),
        ('number_of_visits_down', 'number_of_visits', 'desc'),
    ],
)
def test__date_and_count_sorts_use_f_expressions(mocker, sort_name, field_name, direction):
    """
    Проверяет, что при сортировке по дате и количеству используется выражение F с правильным направлением
    и учётом nulls_first/nulls_last.
    """
    mock_queryset = mocker.Mock(spec=QuerySet)

    mock_f = mocker.Mock()
    if direction == 'asc':
        f_expr = f'{field_name}_asc'
        mock_f.asc.return_value = f_expr
    else:
        f_expr = f'{field_name}_desc'
        mock_f.desc.return_value = f_expr

    mocker.patch('city.sort.F', return_value=mock_f)

    result = apply_sort_to_queryset(mock_queryset, sort_name)

    if direction == 'asc':
        mock_f.asc.assert_called_once_with(nulls_first=True)
    else:
        mock_f.desc.assert_called_once_with(nulls_last=True)

    mock_queryset.order_by.assert_called_once_with(f_expr, 'city__title')
    assert result == mock_queryset.order_by.return_value
