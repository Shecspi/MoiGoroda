from unittest.mock import MagicMock, create_autospec

import pytest
from django.db.models import QuerySet

from collection.filter import apply_filter_to_queryset, filter_visited, filter_not_visited


@pytest.fixture
def mock_queryset():
    """
    Возвращает замоканный QuerySet модели City.
    """
    return create_autospec(QuerySet, instance=True)


def test__filter_visited_applies_correct_filter(mock_queryset):
    """
    Проверяет, что filter_visited вызывает .filter(is_visited=True).
    """
    filter_visited(mock_queryset)
    mock_queryset.filter.assert_called_once_with(is_visited=True)


def test_filter_not_visited_applies_correct_filter(mock_queryset):
    """
    Проверяет, что filter_not_visited вызывает .filter(is_visited=False).
    """
    filter_not_visited(mock_queryset)
    mock_queryset.filter.assert_called_once_with(is_visited=False)


def test_apply_filter_to_queryset_calls_correct_function_for_visited(mock_queryset, monkeypatch):
    """
    Проверяет, что apply_filter_to_queryset вызывает правильную функцию для 'visited'.
    """
    # Создаём мок-результат
    expected_result = MagicMock(name='FilteredQuerySet')

    def mock_filter_visited(qs):
        assert qs is mock_queryset
        return expected_result

    monkeypatch.setitem(
        # Подменяем FILTER_FUNCTIONS словарь временно
        __import__('collection.filter').filter.FILTER_FUNCTIONS,
        'visited',
        mock_filter_visited,
    )

    result = apply_filter_to_queryset(mock_queryset, 'visited')
    assert result is expected_result


def test_apply_filter_to_queryset_raises_on_unknown_filter(mock_queryset):
    """
    Проверяет, что при передаче неизвестного фильтра выбрасывается KeyError.
    """
    with pytest.raises(KeyError, match='Неизвестный фильтр: unknown'):
        apply_filter_to_queryset(mock_queryset, 'unknown')
