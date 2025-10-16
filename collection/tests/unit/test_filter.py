"""
Юнит-тесты для фильтров приложения collection.
"""

from typing import Any
from unittest.mock import MagicMock, create_autospec

import pytest
from django.db.models import QuerySet

from collection.filter import (
    apply_filter_to_queryset,
    filter_visited,
    filter_not_visited,
    FILTER_FUNCTIONS,
)


@pytest.fixture
def mock_queryset() -> Any:
    """Возвращает замоканный QuerySet модели City."""
    return create_autospec(QuerySet, instance=True)


@pytest.mark.unit
class TestFilterFunctions:
    """Тесты для функций фильтрации."""

    def test_filter_visited_applies_correct_filter(self, mock_queryset: Any) -> None:
        """Проверяет что filter_visited вызывает .filter(is_visited=True)."""
        filter_visited(mock_queryset)
        mock_queryset.filter.assert_called_once_with(is_visited=True)

    def test_filter_not_visited_applies_correct_filter(self, mock_queryset: Any) -> None:
        """Проверяет что filter_not_visited вызывает .filter(is_visited=False)."""
        filter_not_visited(mock_queryset)
        mock_queryset.filter.assert_called_once_with(is_visited=False)


@pytest.mark.unit
class TestApplyFilterToQueryset:
    """Тесты для функции apply_filter_to_queryset."""

    def test_apply_filter_calls_correct_function_for_visited(
        self, mock_queryset: Any, monkeypatch: Any
    ) -> None:
        """Проверяет что apply_filter_to_queryset вызывает правильную функцию для 'visited'."""
        expected_result = MagicMock(name='FilteredQuerySet')

        def mock_filter_visited(qs: Any) -> Any:
            assert qs is mock_queryset
            return expected_result

        monkeypatch.setitem(
            FILTER_FUNCTIONS,
            'visited',
            mock_filter_visited,
        )

        result = apply_filter_to_queryset(mock_queryset, 'visited')
        assert result is expected_result

    def test_apply_filter_calls_correct_function_for_not_visited(
        self, mock_queryset: Any, monkeypatch: Any
    ) -> None:
        """Проверяет что apply_filter_to_queryset вызывает правильную функцию для 'not_visited'."""
        expected_result = MagicMock(name='FilteredQuerySet')

        def mock_filter_not_visited(qs: Any) -> Any:
            assert qs is mock_queryset
            return expected_result

        monkeypatch.setitem(
            FILTER_FUNCTIONS,
            'not_visited',
            mock_filter_not_visited,
        )

        result = apply_filter_to_queryset(mock_queryset, 'not_visited')
        assert result is expected_result

    def test_apply_filter_raises_on_unknown_filter(self, mock_queryset: Any) -> None:
        """Проверяет что при передаче неизвестного фильтра выбрасывается KeyError."""
        with pytest.raises(KeyError, match='Неизвестный фильтр: unknown'):
            apply_filter_to_queryset(mock_queryset, 'unknown')

    def test_apply_filter_raises_on_empty_filter(self, mock_queryset: Any) -> None:
        """Проверяет что при передаче пустого фильтра выбрасывается KeyError."""
        with pytest.raises(KeyError, match='Неизвестный фильтр: '):
            apply_filter_to_queryset(mock_queryset, '')


@pytest.mark.unit
class TestFilterFunctionsDict:
    """Тесты для словаря FILTER_FUNCTIONS."""

    def test_filter_functions_contains_visited(self) -> None:
        """Проверяет что FILTER_FUNCTIONS содержит 'visited'."""
        assert 'visited' in FILTER_FUNCTIONS

    def test_filter_functions_contains_not_visited(self) -> None:
        """Проверяет что FILTER_FUNCTIONS содержит 'not_visited'."""
        assert 'not_visited' in FILTER_FUNCTIONS

    def test_filter_functions_visited_is_callable(self) -> None:
        """Проверяет что функция visited является вызываемой."""
        assert callable(FILTER_FUNCTIONS['visited'])

    def test_filter_functions_not_visited_is_callable(self) -> None:
        """Проверяет что функция not_visited является вызываемой."""
        assert callable(FILTER_FUNCTIONS['not_visited'])

    def test_filter_functions_count(self) -> None:
        """Проверяет количество зарегистрированных фильтров."""
        assert len(FILTER_FUNCTIONS) == 2
