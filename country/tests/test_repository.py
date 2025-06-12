import pytest
from unittest.mock import MagicMock, patch

from country.repository import (
    get_countries_with_visited_city,
    get_countries_with_visited_city_in_year,
    get_countries_with_new_visited_city_in_year,
)


@pytest.fixture
def visited_qs_mock():
    return MagicMock(name='VisitedCityQuerySet')


@pytest.fixture
def annotated_qs_mock():
    return MagicMock(name='CountryQuerySet')


@pytest.fixture
def country_manager_mock(annotated_qs_mock):
    manager_mock = MagicMock(name='CountryManager')
    manager_mock.annotate.return_value.filter.return_value.order_by.return_value = annotated_qs_mock
    return manager_mock


@patch('country.repository.Country')
@patch('country.repository.VisitedCity')
def test_get_countries_with_visited_city(
    VisitedCityMock, CountryMock, visited_qs_mock, annotated_qs_mock, country_manager_mock
):
    CountryMock.objects = country_manager_mock
    VisitedCityMock.objects.filter.return_value = visited_qs_mock

    result = get_countries_with_visited_city(user_id=1)

    VisitedCityMock.objects.filter.assert_called_once_with(user_id=1, is_first_visit=True)
    CountryMock.objects.annotate.assert_called_once()
    CountryMock.objects.annotate.return_value.filter.assert_called_once_with(visited_cities__gt=0)
    CountryMock.objects.annotate.return_value.filter.return_value.order_by.assert_called_once_with(
        '-visited_cities'
    )
    assert result == annotated_qs_mock


@patch('country.repository.Country')
@patch('country.repository.VisitedCity')
def test_get_countries_with_visited_city_in_year(
    VisitedCityMock, CountryMock, visited_qs_mock, annotated_qs_mock, country_manager_mock
):
    CountryMock.objects = country_manager_mock
    VisitedCityMock.objects.filter.return_value = visited_qs_mock

    result = get_countries_with_visited_city_in_year(user_id=42, year=2024)

    VisitedCityMock.objects.filter.assert_called_once_with(user_id=42, date_of_visit__year=2024)
    CountryMock.objects.annotate.assert_called_once()
    assert result == annotated_qs_mock


@patch('country.repository.Country')
@patch('country.repository.VisitedCity')
def test_get_countries_with_new_visited_city_in_year(
    VisitedCityMock, CountryMock, visited_qs_mock, annotated_qs_mock, country_manager_mock
):
    CountryMock.objects = country_manager_mock
    VisitedCityMock.objects.filter.return_value = visited_qs_mock

    result = get_countries_with_new_visited_city_in_year(user_id=100, year=2023)

    VisitedCityMock.objects.filter.assert_called_once_with(
        user_id=100, date_of_visit__year=2023, is_first_visit=True
    )
    CountryMock.objects.annotate.assert_called_once()
    assert result == annotated_qs_mock
