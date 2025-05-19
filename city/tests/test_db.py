import pytest
from unittest.mock import patch, MagicMock

from city.services.db import (
    get_all_visited_cities,
    get_number_of_cities,
    get_number_of_visited_cities,
)


@pytest.fixture
def mock_qs():
    mock = MagicMock(name='QuerySet')
    mock.annotate.return_value = mock
    mock.select_related.return_value = mock
    mock.filter.return_value = mock
    return mock


@pytest.fixture
def mock_subquery():
    return MagicMock(name='Subquery')


@pytest.fixture
def mock_exists():
    return MagicMock(name='Exists')


@pytest.fixture
def mock_aggregates():
    with patch('city.services.db.ArrayAgg'), patch('city.services.db.Count'), patch(
        'city.services.db.Avg'
    ), patch('city.services.db.Min'), patch('city.services.db.Max'), patch(
        'city.services.db.Round'
    ), patch('city.services.db.Subquery') as mock_subquery, patch(
        'city.services.db.Exists'
    ) as mock_exists:
        yield {
            'ArrayAgg': mock_subquery,
            'Count': mock_subquery,
            'Avg': mock_subquery,
            'Min': mock_subquery,
            'Max': mock_subquery,
            'Round': mock_subquery,
            'Subquery': mock_subquery,
            'Exists': mock_exists,
        }


@patch('city.services.db.VisitedCity')
def test_get_all_visited_cities_structure(mock_VisitedCity, mock_aggregates):
    """
    Проверяет, что функция корректно строит запрос и использует .filter(), .select_related() и .annotate()
    """
    user_id = 42
    mock_qs = MagicMock()
    mock_VisitedCity.objects.filter.return_value = mock_qs
    mock_qs.select_related.return_value = mock_qs
    mock_qs.annotate.return_value = mock_qs

    result = get_all_visited_cities(user_id)

    # Проверяем, что был хотя бы один вызов filter с is_first_visit
    mock_VisitedCity.objects.filter.assert_any_call(user_id=user_id, is_first_visit=True)
    mock_qs.select_related.assert_called_once_with('city', 'city__region', 'user')
    mock_qs.annotate.assert_called()
    assert result == mock_qs


@patch('city.services.db.VisitedCity')
def test_get_all_visited_cities_annotations(mock_VisitedCity, mock_aggregates):
    """
    Проверяет, что .annotate() вызывается с нужными аргументами.
    """
    user_id = 99
    mock_qs = MagicMock()
    mock_VisitedCity.objects.filter.return_value = mock_qs
    mock_qs.select_related.return_value = mock_qs
    mock_qs.annotate.return_value = mock_qs

    get_all_visited_cities(user_id)

    # Проверяем, что annotate вызывается хотя бы с number_of_visits и has_souvenir
    call_args = mock_qs.annotate.call_args[1]
    assert 'number_of_visits' in call_args
    assert 'has_souvenir' in call_args
    assert 'first_visit_date' in call_args
    assert 'last_visit_date' in call_args
    assert 'visit_dates' in call_args
    assert 'average_rating' in call_args


@patch('city.services.db.City')
def test_get_number_of_cities_returns_count(mock_City):
    """
    Тестирует функцию get_number_of_cities, проверяя, что она корректно
    возвращает количество городов, используя метод count() модели City.

    Мокируется метод count() модели City, чтобы не обращаться к базе данных.
    Проверяется, что метод count() был вызван один раз и что возвращаемое значение
    соответствует ожидаемому.
    """
    mock_City.objects.count.return_value = 123

    result = get_number_of_cities()
    mock_City.objects.count.assert_called_once()

    assert result == 123


@patch('city.services.db.get_all_visited_cities')
def test_get_number_of_visited_cities_returns_count(mock_get_all_visited_cities):
    """
    Тестирует функцию get_number_of_visited_cities, проверяя, что она корректно
    возвращает количество посещённых пользователем городов.

    Мокируется функция get_all_visited_cities, чтобы избежать реальных запросов к базе данных.
    Проверяется, что функция get_all_visited_cities была вызвана с правильным user_id
    и что возвращаемое значение соответствует ожидаемому количеству.
    """
    user_id = 42
    mock_get_all_visited_cities.return_value.count.return_value = 5

    result = get_number_of_visited_cities(user_id)
    mock_get_all_visited_cities.assert_called_once_with(user_id)

    assert result == 5
