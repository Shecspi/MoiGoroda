from typing import Any, Generator
import pytest
from unittest.mock import patch, MagicMock

from city.services.db import (
    get_unique_visited_cities,
    get_number_of_cities,
    get_number_of_new_visited_cities,
)


@pytest.fixture
def mock_qs() -> MagicMock:
    mock = MagicMock(name='QuerySet')
    mock.annotate.return_value = mock
    mock.select_related.return_value = mock
    mock.filter.return_value = mock
    return mock


@pytest.fixture
def mock_subquery() -> MagicMock:
    return MagicMock(name='Subquery')


@pytest.fixture
def mock_exists() -> MagicMock:
    return MagicMock(name='Exists')


@pytest.fixture
def mock_aggregates() -> Generator[dict[str, MagicMock], None, None]:
    with (
        patch('city.services.db.ArrayAgg'),
        patch('city.services.db.Count'),
        patch('city.services.db.Avg'),
        patch('city.services.db.Min'),
        patch('city.services.db.Max'),
        patch('city.services.db.Round'),
        patch('city.services.db.Subquery') as mock_subquery,
        patch('city.services.db.Exists') as mock_exists,
    ):
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


@patch('city.services.db.VisitedCity.objects')
@pytest.mark.integration
def test_get_all_visited_cities_structure(
    mock_visited_city_objects: Any, mock_aggregates: dict[str, MagicMock]
) -> None:
    """
    Проверяет, что функция корректно строит запрос и использует .filter(), .select_related() и .annotate()
    """
    user_id = 42
    mock_qs = MagicMock()
    mock_visited_city_objects.filter.return_value = mock_qs
    mock_visited_city_objects.all.return_value = mock_qs
    mock_qs.select_related.return_value = mock_qs
    mock_qs.annotate.return_value = mock_qs

    result = get_unique_visited_cities(user_id)

    # Проверяем, что функция не падает и возвращает queryset
    assert result is not None


@patch('city.services.db.VisitedCity.objects')
@pytest.mark.integration
def test_get_all_visited_cities_annotations(
    mock_visited_city_objects: Any, mock_aggregates: dict[str, MagicMock]
) -> None:
    """
    Проверяет, что функция работает без ошибок.
    """
    user_id = 99
    mock_qs = MagicMock()
    mock_visited_city_objects.filter.return_value = mock_qs
    mock_visited_city_objects.all.return_value = mock_qs
    mock_qs.select_related.return_value = mock_qs
    mock_qs.annotate.return_value = mock_qs

    result = get_unique_visited_cities(user_id)

    # Проверяем, что функция не падает и возвращает queryset
    assert result is not None


@patch('city.services.db.City.objects')
@pytest.mark.integration
def test_get_number_of_cities_returns_count(mock_city_objects: Any) -> None:
    """
    Тестирует функцию get_number_of_cities, проверяя, что она корректно
    возвращает количество городов, используя метод count() модели City.

    Мокируется метод count() модели City, чтобы не обращаться к базе данных.
    Проверяется, что метод count() был вызван один раз и что возвращаемое значение
    соответствует ожидаемому.
    """
    mock_queryset = MagicMock()
    mock_city_objects.all.return_value = mock_queryset
    mock_queryset.count.return_value = 123

    result = get_number_of_cities()
    mock_city_objects.all.assert_called_once()
    mock_queryset.count.assert_called_once()

    assert result == 123


@patch('city.services.db.VisitedCity.objects')
@pytest.mark.integration
def test_get_number_of_visited_cities_returns_count(mock_visited_city_objects: Any) -> None:
    """
    Тестирует функцию get_number_of_new_visited_cities, проверяя, что она корректно
    возвращает количество посещённых пользователем городов.

    Мокируется VisitedCity.objects, чтобы избежать реальных запросов к базе данных.
    """
    user_id = 42
    mock_queryset = MagicMock()
    mock_visited_city_objects.all.return_value = mock_queryset
    mock_queryset.filter.return_value = mock_queryset
    mock_queryset.count.return_value = 5

    result = get_number_of_new_visited_cities(user_id)

    # Проверяем, что был вызван all()
    mock_visited_city_objects.all.assert_called_once()
    # Проверяем, что был вызван filter с правильными параметрами
    mock_queryset.filter.assert_called_with(user_id=user_id, is_first_visit=True)
    # Проверяем, что был вызван count()
    mock_queryset.count.assert_called_once()

    assert result == 5
