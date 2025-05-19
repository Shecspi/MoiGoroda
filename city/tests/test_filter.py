import pytest
from django.db.models import QuerySet, Q
from city.filter import (
    filter_has_magnet,
    filter_has_no_magnet,
    filter_current_year,
    filter_last_year,
    filter_by_year,
    apply_filter_to_queryset,
    FILTER_FUNCTIONS,
)


def test__filter_has_magnet_applies_correct_filter(mocker):
    """Фильтр возвращает только города с сувенирами (has_souvenir=True)."""
    queryset = mocker.Mock(spec=QuerySet)
    queryset.filter.return_value = 'filtered_result'

    result = filter_has_magnet(queryset, user_id=123)

    queryset.filter.assert_called_once_with(has_souvenir=True)
    assert result == 'filtered_result'


def test__filter_has_no_magnet_applies_correct_filter(mocker):
    """Фильтр возвращает только города без сувениров (has_magnet=False)."""
    queryset = mocker.Mock(spec=QuerySet)
    queryset.filter.return_value = 'filtered_result'

    result = filter_has_no_magnet(queryset, user_id=123)

    queryset.filter.assert_called_once_with(has_magnet=False)
    assert result == 'filtered_result'


def test__filter_current_year_calls_filter_by_year_with_correct_year(mocker):
    """Фильтр текущего года вызывает filter_by_year с текущим годом."""
    mock_date = mocker.patch('city.filter.date')
    mock_date.today.return_value.year = 2025
    mock_filter_by_year = mocker.patch('city.filter.filter_by_year', return_value='filtered')

    result = filter_current_year('queryset', user_id=1)

    mock_filter_by_year.assert_called_once_with('queryset', 1, 2025)
    assert result == 'filtered'


def test__filter_last_year_calls_filter_by_year_with_correct_year(mocker):
    """Фильтр прошлого года вызывает filter_by_year с прошлым годом."""
    mock_date = mocker.patch('city.filter.date')
    mock_date.today.return_value.year = 2025
    mock_filter_by_year = mocker.patch('city.filter.filter_by_year', return_value='filtered')

    result = filter_last_year('queryset', user_id=1)

    mock_filter_by_year.assert_called_once_with('queryset', 1, 2024)
    assert result == 'filtered'


def test__filter_by_year_applies_subqueries_correctly(mocker):
    """filter_by_year применяет нужные Subquery, аннотации и исключения."""
    mock_queryset = mocker.Mock(spec=QuerySet)
    annotated = mocker.Mock()
    filtered = mocker.Mock()
    final_annotated = mocker.Mock()
    mock_queryset.annotate.return_value = annotated
    annotated.exclude.return_value = filtered
    filtered.annotate.return_value = final_annotated

    mock_subquery = mocker.Mock()
    mocker.patch('city.filter.Subquery', return_value=mock_subquery)
    mock_visited_filter = mocker.patch('city.filter.VisitedCity.objects.filter')
    mock_filter_chain = mocker.Mock()
    mock_filter_chain.values.return_value = mock_filter_chain
    mock_filter_chain.annotate.return_value = mock_filter_chain
    mock_visited_filter.return_value = mock_filter_chain

    result = filter_by_year(mock_queryset, user_id=1, year=2023)

    assert result == final_annotated
    mock_queryset.annotate.assert_called_once()
    annotated.exclude.assert_called_once_with(Q(visit_dates=[]))
    filtered.annotate.assert_called_once()


def test__apply_filter_to_queryset_dispatches_correct_function(mocker):
    """apply_filter_to_queryset вызывает правильную функцию из FILTER_FUNCTIONS."""
    mock_filter = mocker.Mock(return_value='filtered')
    mocker.patch.dict('city.filter.FILTER_FUNCTIONS', {'some_filter': mock_filter})

    result = apply_filter_to_queryset('queryset', user_id=42, filter_name='some_filter')

    mock_filter.assert_called_once_with('queryset', 42)
    assert result == 'filtered'


def test__apply_filter_to_queryset_raises_for_unknown_filter():
    """apply_filter_to_queryset выбрасывает KeyError, если фильтр не зарегистрирован."""
    with pytest.raises(KeyError, match='Неизвестный фильтр: unknown'):
        apply_filter_to_queryset(QuerySet(), user_id=1, filter_name='unknown')


@pytest.mark.parametrize('filter_name', FILTER_FUNCTIONS.keys())
def test__all_filters_are_callable_and_registered(mocker, filter_name):
    """Каждая функция-фильтр из FILTER_FUNCTIONS вызывается без ошибок."""
    mock_func = mocker.Mock(return_value='filtered')
    mocker.patch.dict('city.filter.FILTER_FUNCTIONS', {filter_name: mock_func})

    result = apply_filter_to_queryset('queryset', user_id=1, filter_name=filter_name)

    mock_func.assert_called_once_with('queryset', 1)
    assert result == 'filtered'
