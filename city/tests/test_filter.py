from typing import Any
import pytest
from django.db.models import QuerySet, Q
from unittest.mock import Mock
from city.services.filter import (
    filter_has_magnet,
    filter_has_no_magnet,
    filter_current_year,
    filter_last_year,
    filter_by_year,
    apply_filter_to_queryset,
    FILTER_FUNCTIONS,
)


def test__filter_has_magnet_applies_correct_filter(mocker: Any) -> None:
    """Фильтр возвращает только города с сувенирами (has_souvenir=True)."""
    queryset = mocker.Mock(spec=QuerySet)
    queryset.filter.return_value = 'filtered_result'

    result = filter_has_magnet(queryset, user_id=123)

    queryset.filter.assert_called_once_with(has_souvenir=True)
    assert result == 'filtered_result'  # type: ignore


def test__filter_has_no_magnet_applies_correct_filter(mocker: Any) -> None:
    """Фильтр возвращает только города без сувениров (has_souvenir=False)."""
    queryset = mocker.Mock(spec=QuerySet)
    queryset.filter.return_value = 'filtered_result'

    result = filter_has_no_magnet(queryset, user_id=123)

    queryset.filter.assert_called_once_with(has_souvenir=False)
    assert result == 'filtered_result'  # type: ignore


def test__filter_current_year_calls_filter_by_year_with_correct_year(mocker: Any) -> None:
    """Фильтр текущего года вызывает filter_by_year с текущим годом."""
    mock_date = mocker.patch('city.services.filter.date')
    mock_date.today.return_value.year = 2025
    mock_filter_by_year = mocker.patch(
        'city.services.filter.filter_by_year', return_value='filtered'
    )

    mock_queryset = mocker.Mock(spec=QuerySet)
    result = filter_current_year(mock_queryset, user_id=1)

    mock_filter_by_year.assert_called_once_with(mock_queryset, 1, 2025)
    assert result == 'filtered'  # type: ignore


def test__filter_last_year_calls_filter_by_year_with_correct_year(mocker: Any) -> None:
    """Фильтр прошлого года вызывает filter_by_year с прошлым годом."""
    mock_date = mocker.patch('city.services.filter.date')
    mock_date.today.return_value.year = 2025
    mock_filter_by_year = mocker.patch(
        'city.services.filter.filter_by_year', return_value='filtered'
    )

    mock_queryset = mocker.Mock(spec=QuerySet)
    result = filter_last_year(mock_queryset, user_id=1)

    mock_filter_by_year.assert_called_once_with(mock_queryset, 1, 2024)
    assert result == 'filtered'  # type: ignore


def test__filter_by_year_applies_subqueries_correctly(mocker: Any) -> None:
    """filter_by_year применяет нужные Subquery, аннотации и исключения."""
    mock_queryset = mocker.Mock(spec=QuerySet)
    annotated = mocker.Mock()
    filtered = mocker.Mock()
    final_annotated = mocker.Mock()
    mock_queryset.annotate.return_value = annotated
    annotated.exclude.return_value = filtered
    filtered.annotate.return_value = final_annotated

    mock_subquery = mocker.Mock()
    mocker.patch('city.services.filter.Subquery', return_value=mock_subquery)
    mock_visited_filter = mocker.patch('city.services.filter.VisitedCity.objects.filter')
    mock_filter_chain = mocker.Mock()
    mock_filter_chain.values.return_value = mock_filter_chain
    mock_filter_chain.annotate.return_value = mock_filter_chain
    mock_visited_filter.return_value = mock_filter_chain

    result = filter_by_year(mock_queryset, user_id=1, year=2023)

    assert result == final_annotated
    mock_queryset.annotate.assert_called_once()
    annotated.exclude.assert_called_once_with(Q(visit_dates=[]))
    filtered.annotate.assert_called_once()


def test__apply_filter_to_queryset_dispatches_correct_function(mocker: Any) -> None:
    """apply_filter_to_queryset вызывает правильную функцию из FILTER_FUNCTIONS."""
    mock_filter = mocker.Mock(return_value='filtered')
    mocker.patch.dict('city.services.filter.FILTER_FUNCTIONS', {'some_filter': mock_filter})

    mock_queryset = mocker.Mock(spec=QuerySet)
    result = apply_filter_to_queryset(mock_queryset, user_id=42, filter_name='some_filter')

    mock_filter.assert_called_once_with(mock_queryset, 42)
    assert result == 'filtered'  # type: ignore


def test__apply_filter_to_queryset_raises_for_unknown_filter() -> None:
    """apply_filter_to_queryset выбрасывает KeyError, если фильтр не зарегистрирован."""
    with pytest.raises(KeyError, match='Неизвестный фильтр: unknown'):
        apply_filter_to_queryset(QuerySet(), user_id=1, filter_name='unknown')  # type: ignore


@pytest.mark.parametrize('filter_name', FILTER_FUNCTIONS.keys())
def test__all_filters_are_callable_and_registered(mocker: Any, filter_name: str) -> None:
    """Каждая функция-фильтр из FILTER_FUNCTIONS вызывается без ошибок."""
    mock_func = mocker.Mock(return_value='filtered')
    mocker.patch.dict('city.services.filter.FILTER_FUNCTIONS', {filter_name: mock_func})

    mock_queryset = mocker.Mock(spec=QuerySet)
    result = apply_filter_to_queryset(mock_queryset, user_id=1, filter_name=filter_name)

    mock_func.assert_called_once_with(mock_queryset, 1)
    assert result == 'filtered'  # type: ignore


def test__filter_by_year_with_different_years(mocker: Any) -> None:
    """Тест filter_by_year с разными годами."""
    mock_queryset = mocker.Mock(spec=QuerySet)
    annotated = mocker.Mock()
    filtered = mocker.Mock()
    final_annotated = mocker.Mock()
    mock_queryset.annotate.return_value = annotated
    annotated.exclude.return_value = filtered
    filtered.annotate.return_value = final_annotated

    mock_subquery = mocker.Mock()
    mocker.patch('city.services.filter.Subquery', return_value=mock_subquery)
    mock_visited_filter = mocker.patch('city.services.filter.VisitedCity.objects.filter')
    mock_filter_chain = mocker.Mock()
    mock_filter_chain.values.return_value = mock_filter_chain
    mock_filter_chain.annotate.return_value = mock_filter_chain
    mock_visited_filter.return_value = mock_filter_chain

    # Тестируем с разными годами
    years_to_test = [2020, 2021, 2022, 2023, 2024]

    for year in years_to_test:
        result = filter_by_year(mock_queryset, user_id=1, year=year)
        assert result == final_annotated


def test__filter_by_year_subquery_calls(mocker: Any) -> None:
    """Тест детального вызова Subquery в filter_by_year."""
    mock_queryset = mocker.Mock(spec=QuerySet)
    annotated = mocker.Mock()
    filtered = mocker.Mock()
    final_annotated = mocker.Mock()
    mock_queryset.annotate.return_value = annotated
    annotated.exclude.return_value = filtered
    filtered.annotate.return_value = final_annotated

    mock_subquery = mocker.Mock()
    mock_subquery_patch = mocker.patch('city.services.filter.Subquery', return_value=mock_subquery)
    mock_visited_filter = mocker.patch('city.services.filter.VisitedCity.objects.filter')
    mock_filter_chain = mocker.Mock()
    mock_filter_chain.values.return_value = mock_filter_chain
    mock_filter_chain.annotate.return_value = mock_filter_chain
    mock_visited_filter.return_value = mock_filter_chain

    result = filter_by_year(mock_queryset, user_id=42, year=2023)

    # Проверяем, что Subquery вызывался несколько раз (для разных подзапросов)
    assert (
        mock_subquery_patch.call_count >= 4
    )  # visit_dates, first_visit_date, last_visit_date, number_of_visits
    assert result == final_annotated


def test__apply_filter_to_queryset_with_empty_filter_name() -> None:
    """Тест apply_filter_to_queryset с пустым именем фильтра."""
    with pytest.raises(KeyError, match='Неизвестный фильтр: '):
        apply_filter_to_queryset(QuerySet(), user_id=1, filter_name='')  # type: ignore


def test__apply_filter_to_queryset_with_none_filter_name() -> None:
    """Тест apply_filter_to_queryset с None именем фильтра."""
    with pytest.raises(KeyError, match='Неизвестный фильтр: None'):
        apply_filter_to_queryset(QuerySet(), user_id=1, filter_name=None)  # type: ignore


def test__filter_has_magnet_with_different_user_ids(mocker: Any) -> None:
    """Тест filter_has_magnet с разными user_id."""
    queryset = mocker.Mock(spec=QuerySet)
    queryset.filter.return_value = 'filtered_result'

    # user_id не используется в filter_has_magnet, но тестируем передачу параметра
    user_ids = [1, 42, 999, 0, -1]

    for user_id in user_ids:
        result = filter_has_magnet(queryset, user_id=user_id)
        queryset.filter.assert_called_with(has_souvenir=True)
        assert result == 'filtered_result'  # type: ignore


def test__filter_has_no_magnet_with_different_user_ids(mocker: Any) -> None:
    """Тест filter_has_no_magnet с разными user_id."""
    queryset = mocker.Mock(spec=QuerySet)
    queryset.filter.return_value = 'filtered_result'

    # user_id не используется в filter_has_no_magnet, но тестируем передачу параметра
    user_ids = [1, 42, 999, 0, -1]

    for user_id in user_ids:
        result = filter_has_no_magnet(queryset, user_id=user_id)
        queryset.filter.assert_called_with(has_souvenir=False)
        assert result == 'filtered_result'  # type: ignore


def test__filter_current_year_edge_cases(mocker: Any) -> None:
    """Тест filter_current_year с граничными случаями."""
    mock_date = mocker.patch('city.services.filter.date')
    mock_filter_by_year = mocker.patch(
        'city.services.filter.filter_by_year', return_value='filtered'
    )

    # Тест с разными годами
    test_years = [2000, 2020, 2024, 2030, 2100]

    for year in test_years:
        mock_date.today.return_value.year = year
        mock_queryset = mocker.Mock(spec=QuerySet)
        result = filter_current_year(mock_queryset, user_id=1)
        mock_filter_by_year.assert_called_with(mock_queryset, 1, year)
        assert result == 'filtered'  # type: ignore


def test__filter_last_year_edge_cases(mocker: Any) -> None:
    """Тест filter_last_year с граничными случаями."""
    mock_date = mocker.patch('city.services.filter.date')
    mock_filter_by_year = mocker.patch(
        'city.services.filter.filter_by_year', return_value='filtered'
    )

    # Тест с разными годами
    test_years = [2001, 2021, 2025, 2031, 2101]

    for year in test_years:
        mock_date.today.return_value.year = year
        mock_queryset = mocker.Mock(spec=QuerySet)
        result = filter_last_year(mock_queryset, user_id=1)
        mock_filter_by_year.assert_called_with(mock_queryset, 1, year - 1)
        assert result == 'filtered'  # type: ignore


def test__filter_by_year_with_edge_case_years(mocker: Any) -> None:
    """Тест filter_by_year с граничными годами."""
    mock_queryset = mocker.Mock(spec=QuerySet)
    annotated = mocker.Mock()
    filtered = mocker.Mock()
    final_annotated = mocker.Mock()
    mock_queryset.annotate.return_value = annotated
    annotated.exclude.return_value = filtered
    filtered.annotate.return_value = final_annotated

    mock_subquery = mocker.Mock()
    mocker.patch('city.services.filter.Subquery', return_value=mock_subquery)
    mock_visited_filter = mocker.patch('city.services.filter.VisitedCity.objects.filter')
    mock_filter_chain = mocker.Mock()
    mock_filter_chain.values.return_value = mock_filter_chain
    mock_filter_chain.annotate.return_value = mock_filter_chain
    mock_visited_filter.return_value = mock_filter_chain

    # Тестируем граничные случаи
    edge_years = [1900, 1999, 2000, 2024, 2099, 2100]

    for year in edge_years:
        result = filter_by_year(mock_queryset, user_id=1, year=year)
        assert result == final_annotated


def test__filter_by_year_with_different_user_ids(mocker: Any) -> None:
    """Тест filter_by_year с разными user_id."""
    mock_queryset = mocker.Mock(spec=QuerySet)
    annotated = mocker.Mock()
    filtered = mocker.Mock()
    final_annotated = mocker.Mock()
    mock_queryset.annotate.return_value = annotated
    annotated.exclude.return_value = filtered
    filtered.annotate.return_value = final_annotated

    mock_subquery = mocker.Mock()
    mocker.patch('city.services.filter.Subquery', return_value=mock_subquery)
    mock_visited_filter = mocker.patch('city.services.filter.VisitedCity.objects.filter')
    mock_filter_chain = mocker.Mock()
    mock_filter_chain.values.return_value = mock_filter_chain
    mock_filter_chain.annotate.return_value = mock_filter_chain
    mock_visited_filter.return_value = mock_filter_chain

    # Тестируем с разными user_id
    user_ids = [1, 42, 999, 0, -1]

    for user_id in user_ids:
        result = filter_by_year(mock_queryset, user_id=user_id, year=2023)
        assert result == final_annotated


def test__filter_functions_keys_are_strings() -> None:
    """Тест, что ключи в FILTER_FUNCTIONS являются строками."""
    for key in FILTER_FUNCTIONS.keys():
        assert isinstance(key, str)
        assert len(key) > 0


def test__filter_functions_values_are_callable() -> None:
    """Тест, что значения в FILTER_FUNCTIONS являются вызываемыми."""
    for value in FILTER_FUNCTIONS.values():
        assert callable(value)


def test__filter_functions_not_empty() -> None:
    """Тест, что FILTER_FUNCTIONS не пустой."""
    assert len(FILTER_FUNCTIONS) > 0


def test__filter_functions_expected_keys() -> None:
    """Тест, что FILTER_FUNCTIONS содержит ожидаемые ключи."""
    expected_keys = {'magnet', 'no_magnet', 'current_year', 'last_year'}
    actual_keys = set(FILTER_FUNCTIONS.keys())
    assert actual_keys == expected_keys
