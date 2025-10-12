"""
Юнит-тесты для repository приложения country.
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from country.repository import (
    get_countries_with_visited_city,
    get_countries_with_visited_city_in_year,
    get_countries_with_new_visited_city_in_year,
)


@pytest.fixture
def visited_qs_mock() -> Any:
    """Возвращает мок VisitedCity QuerySet."""
    return MagicMock(name='VisitedCityQuerySet')


@pytest.fixture
def annotated_qs_mock() -> Any:
    """Возвращает мок Country QuerySet."""
    return MagicMock(name='CountryQuerySet')


@pytest.fixture
def country_manager_mock(annotated_qs_mock: Any) -> Any:
    """Возвращает мок Country Manager."""
    manager_mock = MagicMock(name='CountryManager')
    manager_mock.annotate.return_value.filter.return_value.order_by.return_value = annotated_qs_mock
    return manager_mock


@pytest.mark.unit
class TestGetCountriesWithVisitedCity:
    """Тесты для функции get_countries_with_visited_city."""

    @patch('country.repository.Country')
    @patch('country.repository.VisitedCity')
    def test_calls_correct_filters(
        self,
        visited_city_mock: Any,
        country_mock: Any,
        visited_qs_mock: Any,
        annotated_qs_mock: Any,
        country_manager_mock: Any,
    ) -> None:
        """Проверяет что вызываются правильные фильтры."""
        country_mock.objects = country_manager_mock
        visited_city_mock.objects.filter.return_value = visited_qs_mock

        result = get_countries_with_visited_city(user_id=1)

        visited_city_mock.objects.filter.assert_called_once_with(user_id=1, is_first_visit=True)
        country_mock.objects.annotate.assert_called_once()
        assert result == annotated_qs_mock

    @patch('country.repository.Country')
    @patch('country.repository.VisitedCity')
    def test_filters_by_visited_cities_gt_zero(
        self,
        visited_city_mock: Any,
        country_mock: Any,
        country_manager_mock: Any,
    ) -> None:
        """Проверяет фильтрацию по visited_cities > 0."""
        country_mock.objects = country_manager_mock
        visited_city_mock.objects.filter.return_value = MagicMock()

        get_countries_with_visited_city(user_id=42)

        country_mock.objects.annotate.return_value.filter.assert_called_once_with(
            visited_cities__gt=0
        )

    @patch('country.repository.Country')
    @patch('country.repository.VisitedCity')
    def test_orders_by_visited_cities_desc(
        self,
        visited_city_mock: Any,
        country_mock: Any,
        country_manager_mock: Any,
    ) -> None:
        """Проверяет сортировку по убыванию visited_cities."""
        country_mock.objects = country_manager_mock
        visited_city_mock.objects.filter.return_value = MagicMock()

        get_countries_with_visited_city(user_id=5)

        country_mock.objects.annotate.return_value.filter.return_value.order_by.assert_called_once_with(
            '-visited_cities'
        )


@pytest.mark.unit
class TestGetCountriesWithVisitedCityInYear:
    """Тесты для функции get_countries_with_visited_city_in_year."""

    @patch('country.repository.Country')
    @patch('country.repository.VisitedCity')
    def test_filters_by_year(
        self,
        visited_city_mock: Any,
        country_mock: Any,
        country_manager_mock: Any,
    ) -> None:
        """Проверяет фильтрацию по году."""
        country_mock.objects = country_manager_mock
        visited_city_mock.objects.filter.return_value = MagicMock()

        get_countries_with_visited_city_in_year(user_id=42, year=2024)

        visited_city_mock.objects.filter.assert_called_once_with(
            user_id=42, date_of_visit__year=2024
        )


@pytest.mark.unit
class TestGetCountriesWithNewVisitedCityInYear:
    """Тесты для функции get_countries_with_new_visited_city_in_year."""

    @patch('country.repository.Country')
    @patch('country.repository.VisitedCity')
    def test_filters_by_year_and_first_visit(
        self,
        visited_city_mock: Any,
        country_mock: Any,
        country_manager_mock: Any,
    ) -> None:
        """Проверяет фильтрацию по году и первому посещению."""
        country_mock.objects = country_manager_mock
        visited_city_mock.objects.filter.return_value = MagicMock()

        get_countries_with_new_visited_city_in_year(user_id=100, year=2023)

        visited_city_mock.objects.filter.assert_called_once_with(
            user_id=100, date_of_visit__year=2023, is_first_visit=True
        )

