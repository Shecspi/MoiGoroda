"""
Тесты для модуля сортировки city/services/sort.py
"""

from typing import Any
import pytest
from django.db.models import QuerySet
from unittest.mock import Mock

from city.services.sort import SORT_FUNCTIONS, apply_sort_to_queryset
from city.models import VisitedCity


@pytest.mark.parametrize('sort_name', SORT_FUNCTIONS.keys())
@pytest.mark.unit
def test__apply_sort_to_queryset_calls_correct_function(mocker: Any, sort_name: str) -> None:
    """
    Проверяет, что apply_sort_to_queryset вызывает соответствующую функцию из SORT_FUNCTIONS.
    """
    mock_queryset = mocker.Mock(spec=QuerySet[VisitedCity])
    mock_func = mocker.Mock(return_value='sorted_queryset')
    mocker.patch.dict('city.services.sort.SORT_FUNCTIONS', {sort_name: mock_func})

    result = apply_sort_to_queryset(mock_queryset, sort_name)

    mock_func.assert_called_once_with(mock_queryset)
    assert result == 'sorted_queryset'  # type: ignore


@pytest.mark.unit
def test__apply_sort_to_queryset_raises_for_unknown_sort(mocker: Any) -> None:
    """
    Проверяет, что при неизвестном параметре сортировки вызывается KeyError.
    """
    mock_queryset = mocker.Mock(spec=QuerySet[VisitedCity])

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
@pytest.mark.unit
def test__name_sorts_call_order_by_correctly(
    mocker: Any, sort_name: str, expected_order_by_args: tuple[str, ...]
) -> None:
    """
    Проверяет, что сортировка по имени вызывает order_by с корректными аргументами.
    """
    mock_queryset = mocker.Mock(spec=QuerySet[VisitedCity])
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
@pytest.mark.unit
def test__date_and_count_sorts_use_f_expressions(
    mocker: Any, sort_name: str, field_name: str, direction: str
) -> None:
    """
    Проверяет, что при сортировке по дате и количеству используется выражение F с правильным направлением
    и учётом nulls_first/nulls_last.
    """
    mock_queryset = mocker.Mock(spec=QuerySet[VisitedCity])

    mock_f = mocker.Mock()
    if direction == 'asc':
        f_expr = f'{field_name}_asc'
        mock_f.asc.return_value = f_expr
    else:
        f_expr = f'{field_name}_desc'
        mock_f.desc.return_value = f_expr

    mocker.patch('city.services.sort.F', return_value=mock_f)

    result = apply_sort_to_queryset(mock_queryset, sort_name)

    if direction == 'asc':
        mock_f.asc.assert_called_once_with(nulls_first=True)
    else:
        mock_f.desc.assert_called_once_with(nulls_last=True)

    mock_queryset.order_by.assert_called_once_with(f_expr, 'city__title')
    assert result == mock_queryset.order_by.return_value


@pytest.mark.parametrize(
    'sort_name, field_name, direction',
    [
        ('date_of_foundation_up', 'city__date_of_foundation', 'asc'),
        ('date_of_foundation_down', 'city__date_of_foundation', 'desc'),
        ('number_of_users_who_visit_city_up', 'number_of_users_who_visit_city', 'asc'),
        ('number_of_users_who_visit_city_down', 'number_of_users_who_visit_city', 'desc'),
        ('number_of_visits_all_users_up', 'number_of_visits_all_users', 'asc'),
        ('number_of_visits_all_users_down', 'number_of_visits_all_users', 'desc'),
    ],
)
@pytest.mark.unit
def test__additional_sorts_use_f_expressions(
    mocker: Any, sort_name: str, field_name: str, direction: str
) -> None:
    """
    Проверяет, что при сортировке по дополнительным полям используется выражение F с правильным направлением.
    """
    mock_queryset = mocker.Mock(spec=QuerySet[VisitedCity])

    mock_f = mocker.Mock()
    if direction == 'asc':
        f_expr = f'{field_name}_asc'
        mock_f.asc.return_value = f_expr
    else:
        f_expr = f'{field_name}_desc'
        mock_f.desc.return_value = f_expr

    mocker.patch('city.services.sort.F', return_value=mock_f)

    result = apply_sort_to_queryset(mock_queryset, sort_name)

    if direction == 'asc':
        # Для некоторых полей используется nulls_last=True
        if field_name in ['city__date_of_foundation']:
            mock_f.asc.assert_called_once_with(nulls_last=True)
        else:
            mock_f.asc.assert_called_once_with(nulls_last=True)
    else:
        mock_f.desc.assert_called_once_with(nulls_last=True)

    mock_queryset.order_by.assert_called_once_with(f_expr, 'city__title')
    assert result == mock_queryset.order_by.return_value


@pytest.mark.unit
def test__sort_functions_dict_structure() -> None:
    """
    Проверяет, что SORT_FUNCTIONS содержит все ожидаемые функции сортировки.
    """
    expected_sorts = {
        'name_down',
        'name_up',
        'first_visit_date_down',
        'first_visit_date_up',
        'last_visit_date_down',
        'last_visit_date_up',
        'number_of_visits_down',
        'number_of_visits_up',
        'date_of_foundation_down',
        'date_of_foundation_up',
        'number_of_users_who_visit_city_down',
        'number_of_users_who_visit_city_up',
        'number_of_visits_all_users_down',
        'number_of_visits_all_users_up',
    }

    actual_sorts = set(SORT_FUNCTIONS.keys())
    assert actual_sorts == expected_sorts


@pytest.mark.unit
def test__sort_functions_are_callable() -> None:
    """
    Проверяет, что все функции в SORT_FUNCTIONS являются вызываемыми.
    """
    for sort_name, sort_func in SORT_FUNCTIONS.items():
        assert callable(sort_func), f'Функция {sort_name} не является вызываемой'


@pytest.mark.unit
def test__apply_sort_to_queryset_with_none_queryset() -> None:
    """
    Проверяет, что apply_sort_to_queryset корректно обрабатывает None queryset.
    """
    with pytest.raises(AttributeError):
        apply_sort_to_queryset(None, 'name_up')  # type: ignore


@pytest.mark.unit
def test__apply_sort_to_queryset_with_empty_sort_name() -> None:
    """
    Проверяет, что apply_sort_to_queryset корректно обрабатывает пустое имя сортировки.
    """
    mock_queryset = Mock(spec=QuerySet[VisitedCity])

    with pytest.raises(KeyError) as exc_info:
        apply_sort_to_queryset(mock_queryset, '')

    assert 'Неизвестный параметр сортировки' in str(exc_info.value)


@pytest.mark.unit
def test__apply_sort_to_queryset_with_none_sort_name() -> None:
    """
    Проверяет, что apply_sort_to_queryset корректно обрабатывает None имя сортировки.
    """
    mock_queryset = Mock(spec=QuerySet[VisitedCity])

    with pytest.raises(KeyError) as exc_info:
        apply_sort_to_queryset(mock_queryset, None)  # type: ignore

    assert 'Неизвестный параметр сортировки' in str(exc_info.value)


@pytest.mark.parametrize(
    'sort_name',
    [
        'name_up',
        'name_down',
        'first_visit_date_up',
        'first_visit_date_down',
        'last_visit_date_up',
        'last_visit_date_down',
        'number_of_visits_up',
        'number_of_visits_down',
        'date_of_foundation_up',
        'date_of_foundation_down',
        'number_of_users_who_visit_city_up',
        'number_of_users_who_visit_city_down',
        'number_of_visits_all_users_up',
        'number_of_visits_all_users_down',
    ],
)
@pytest.mark.unit
def test__all_sort_functions_return_queryset(mocker: Any, sort_name: str) -> None:
    """
    Проверяет, что все функции сортировки возвращают QuerySet.
    """
    mock_queryset = mocker.Mock(spec=QuerySet[VisitedCity])
    mock_queryset.order_by.return_value = mock_queryset

    result = apply_sort_to_queryset(mock_queryset, sort_name)

    assert result == mock_queryset
    mock_queryset.order_by.assert_called_once()


@pytest.mark.unit
def test__sort_functions_import() -> None:
    """
    Проверяет, что все необходимые функции импортированы корректно.
    """
    from city.services.sort import (
        apply_sort_to_queryset,
        sort_by_name_up,
        sort_by_name_down,
        sort_by_first_visit_date_up,
        sort_by_first_visit_date_down,
        sort_by_last_visit_date_up,
        sort_by_last_visit_date_down,
        sort_number_of_visits_up,
        sort_number_of_visits_down,
        date_of_foundation_up,
        date_of_foundation_down,
        number_of_users_who_visit_city_up,
        number_of_users_who_visit_city_down,
        number_of_visits_all_users_up,
        number_of_visits_all_users_down,
        SORT_FUNCTIONS,
    )

    # Проверяем, что все функции импортированы
    assert callable(apply_sort_to_queryset)
    assert callable(sort_by_name_up)
    assert callable(sort_by_name_down)
    assert callable(sort_by_first_visit_date_up)
    assert callable(sort_by_first_visit_date_down)
    assert callable(sort_by_last_visit_date_up)
    assert callable(sort_by_last_visit_date_down)
    assert callable(sort_number_of_visits_up)
    assert callable(sort_number_of_visits_down)
    assert callable(date_of_foundation_up)
    assert callable(date_of_foundation_down)
    assert callable(number_of_users_who_visit_city_up)
    assert callable(number_of_users_who_visit_city_down)
    assert callable(number_of_visits_all_users_up)
    assert callable(number_of_visits_all_users_down)
    assert isinstance(SORT_FUNCTIONS, dict)
