"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from unittest.mock import Mock, patch

from dashboard.api import (
    GetTotalVisitedCountriesController,
    GetUsersWithVisitedCountriesController,
    GetAverageQtyVisitedCountriesController,
    GetMaxQtyVisitedCountriesController,
    GetAddedVisitedCountryController,
    GetAddedVisitedCountriesChartController,
)


# ===== Unit тесты для API endpoints =====


@pytest.mark.unit
def test_get_total_visited_countries_has_correct_permissions() -> None:
    """Тест что GetTotalVisitedCountries требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetTotalVisitedCountriesController()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_total_visited_countries_has_correct_http_methods() -> None:
    """Тест что GetTotalVisitedCountries разрешает только GET"""
    view = GetTotalVisitedCountriesController()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_get_users_with_visited_countries_has_correct_permissions() -> None:
    """Тест что GetUsersWithVisitedCountries требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetUsersWithVisitedCountriesController()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_users_with_visited_countries_has_correct_http_methods() -> None:
    """Тест что GetUsersWithVisitedCountries разрешает только GET"""
    view = GetUsersWithVisitedCountriesController()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_get_average_qty_visited_countries_has_correct_permissions() -> None:
    """Тест что GetAverageQtyVisitedCountries требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetAverageQtyVisitedCountriesController()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_average_qty_visited_countries_has_correct_http_methods() -> None:
    """Тест что GetAverageQtyVisitedCountries разрешает только GET"""
    view = GetAverageQtyVisitedCountriesController()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_get_max_qty_visited_countries_has_correct_permissions() -> None:
    """Тест что GetMaxQtyVisitedCountries требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetMaxQtyVisitedCountriesController()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_max_qty_visited_countries_has_correct_http_methods() -> None:
    """Тест что GetMaxQtyVisitedCountries разрешает только GET"""
    view = GetMaxQtyVisitedCountriesController()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_get_added_visited_country_yesterday_has_correct_permissions() -> None:
    """Тест что GetAddedVisitedCountryYeterday требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetAddedVisitedCountryController()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_added_visited_country_yesterday_has_correct_http_methods() -> None:
    """Тест что GetAddedVisitedCountryYeterday разрешает только GET"""
    view = GetAddedVisitedCountryController()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_get_added_visited_countries_chart_has_correct_permissions() -> None:
    """Тест что GetAddedVisitedCountriesChart требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetAddedVisitedCountriesChartController()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_added_visited_countries_chart_has_correct_http_methods() -> None:
    """Тест что GetAddedVisitedCountriesChart разрешает только GET"""
    view = GetAddedVisitedCountriesChartController()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_all_api_views_inherit_from_list_api_view() -> None:
    """Тест что все API вьюхи наследуются от ListAPIView"""
    from rest_framework import generics

    views = [
        GetTotalVisitedCountriesController,
        GetUsersWithVisitedCountriesController,
        GetAverageQtyVisitedCountriesController,
        GetMaxQtyVisitedCountriesController,
        GetAddedVisitedCountryController,
        GetAddedVisitedCountriesChartController,
    ]

    for view_class in views:
        assert issubclass(view_class, generics.ListAPIView)


@pytest.mark.unit
def test_get_total_visited_countries_response_structure() -> None:
    """Тест структуры ответа GetTotalVisitedCountries"""
    view = GetTotalVisitedCountriesController()

    with patch('dashboard.api.VisitedCountry.objects') as mock_objects:
        mock_objects.count.return_value = 42

        request = Mock()
        response = view.get(request)

        assert 'count' in response.data
        assert response.data['count'] == 42


@pytest.mark.unit
def test_get_users_with_visited_countries_response_structure() -> None:
    """Тест структуры ответа GetUsersWithVisitedCountries"""
    view = GetUsersWithVisitedCountriesController()
    view.queryset = Mock()

    with patch.object(view.queryset, 'values') as mock_values:
        mock_distinct = Mock()
        mock_distinct.count.return_value = 15
        mock_values.return_value.distinct.return_value = mock_distinct

        request = Mock()
        response = view.get(request)

        assert 'count' in response.data
        assert response.data['count'] == 15


@pytest.mark.unit
def test_get_average_qty_visited_countries_calculates_correctly() -> None:
    """Тест правильности расчета среднего количества стран"""
    view = GetAverageQtyVisitedCountriesController()
    view.queryset = Mock()

    with patch.object(view.queryset, 'count', return_value=100):
        with patch.object(view.queryset, 'values') as mock_values:
            mock_distinct = Mock()
            mock_distinct.count.return_value = 10
            mock_values.return_value.distinct.return_value = mock_distinct

            request = Mock()
            response = view.get(request)

            # 100 стран / 10 пользователей = 10
            assert response.data['count'] == 10


@pytest.mark.unit
def test_get_max_qty_visited_countries_response_structure() -> None:
    """Тест структуры ответа GetMaxQtyVisitedCountries"""
    view = GetMaxQtyVisitedCountriesController()
    view.queryset = Mock()

    with patch.object(view.queryset, 'values') as mock_values:
        mock_annotate = Mock()
        mock_annotate.aggregate.return_value = {'value': 25}
        mock_values.return_value.annotate.return_value = mock_annotate

        request = Mock()
        response = view.get(request)

        assert 'count' in response.data
        assert response.data['count'] == 25


@pytest.mark.unit
def test_get_added_visited_country_yesterday_uses_days_param() -> None:
    """Тест что GetAddedVisitedCountryYeterday использует параметр days"""
    view = GetAddedVisitedCountryController()
    view.queryset = Mock()
    view.kwargs = {'days': 7}

    with patch.object(view.queryset, 'filter') as mock_filter:
        mock_filter.return_value.count.return_value = 5

        request = Mock()
        response = view.get(request)

        assert response.data['count'] == 5
        mock_filter.assert_called_once()


@pytest.mark.unit
def test_get_added_visited_countries_chart_response_is_list() -> None:
    """Тест что GetAddedVisitedCountriesChart возвращает список"""
    view = GetAddedVisitedCountriesChartController()
    view.queryset = Mock()

    mock_data = [
        {'label': '01.01.2024', 'count': 5},
        {'label': '02.01.2024', 'count': 3},
    ]

    with patch.object(view.queryset, 'annotate') as mock_annotate:
        mock_annotate.return_value.order_by.return_value.annotate.return_value.values.return_value.annotate.return_value.__getitem__.return_value = mock_data

        request = Mock()
        response = view.get(request)

        assert isinstance(response.data, list)
