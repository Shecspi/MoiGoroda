import pytest
from unittest.mock import MagicMock

from django.db.models import F

from region.services.sort import SORT_FUNCTIONS, apply_sort_to_queryset


@pytest.mark.parametrize('sort_key', list(SORT_FUNCTIONS.keys()))
def test_sort_function_applies_expected_order(sort_key):
    # Arrange
    queryset = MagicMock()
    expected_order = {
        'name_up': ('title', '-is_visited'),
        'name_down': ('-title', '-is_visited'),
        'first_visit_date_up': ('-is_visited', F('first_visit_date').asc(nulls_first=True)),
        'first_visit_date_down': ('-is_visited', F('first_visit_date').desc(nulls_last=True)),
        'last_visit_date_up': ('-is_visited', F('last_visit_date').asc(nulls_first=True)),
        'last_visit_date_down': ('-is_visited', F('last_visit_date').desc(nulls_last=True)),
    }[sort_key]

    # Act
    result = apply_sort_to_queryset(queryset, sort_key, True)

    # Assert
    queryset.order_by.assert_called_once_with(*expected_order)
    assert result == queryset.order_by.return_value


def test_apply_sort_to_queryset_unauthenticated_calls_default():
    queryset = MagicMock()

    result = apply_sort_to_queryset(queryset, 'name_up', False)

    # Проверяем, что вызывается sort_for_not_authenticated
    queryset.order_by.assert_called_once_with('title')
    assert result == queryset.order_by.return_value


def test_apply_sort_to_queryset_invalid_key_raises():
    queryset = MagicMock()

    with pytest.raises(KeyError, match='Неизвестный параметр сортировки: wrong_key'):
        apply_sort_to_queryset(queryset, 'wrong_key', True)
