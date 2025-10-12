"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from unittest.mock import Mock, patch

from dashboard.api import (
    GetTotalVisitedCountries,
    GetUsersWithVisitedCountries,
    GetAverageQtyVisitedCountries,
    GetMaxQtyVisitedCountries,
    GetAddedVisitedCountryYeterday,
    GetAddedVisitedCountriesByDay,
)


# ===== Unit тесты для API endpoints =====


@pytest.mark.unit
def test_get_total_visited_countries_has_correct_permissions() -> None:
    """Тест что GetTotalVisitedCountries требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetTotalVisitedCountries()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_total_visited_countries_has_correct_http_methods() -> None:
    """Тест что GetTotalVisitedCountries разрешает только GET"""
    view = GetTotalVisitedCountries()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_get_users_with_visited_countries_has_correct_permissions() -> None:
    """Тест что GetUsersWithVisitedCountries требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetUsersWithVisitedCountries()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_users_with_visited_countries_has_correct_http_methods() -> None:
    """Тест что GetUsersWithVisitedCountries разрешает только GET"""
    view = GetUsersWithVisitedCountries()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_get_average_qty_visited_countries_has_correct_permissions() -> None:
    """Тест что GetAverageQtyVisitedCountries требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetAverageQtyVisitedCountries()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_average_qty_visited_countries_has_correct_http_methods() -> None:
    """Тест что GetAverageQtyVisitedCountries разрешает только GET"""
    view = GetAverageQtyVisitedCountries()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_get_max_qty_visited_countries_has_correct_permissions() -> None:
    """Тест что GetMaxQtyVisitedCountries требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetMaxQtyVisitedCountries()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_max_qty_visited_countries_has_correct_http_methods() -> None:
    """Тест что GetMaxQtyVisitedCountries разрешает только GET"""
    view = GetMaxQtyVisitedCountries()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_get_added_visited_country_yesterday_has_correct_permissions() -> None:
    """Тест что GetAddedVisitedCountryYeterday требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetAddedVisitedCountryYeterday()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_added_visited_country_yesterday_has_correct_http_methods() -> None:
    """Тест что GetAddedVisitedCountryYeterday разрешает только GET"""
    view = GetAddedVisitedCountryYeterday()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_get_added_visited_countries_by_day_has_correct_permissions() -> None:
    """Тест что GetAddedVisitedCountriesByDay требует правильные пермишены"""
    from rest_framework.permissions import IsAuthenticated, IsAdminUser

    view = GetAddedVisitedCountriesByDay()
    assert IsAuthenticated in view.permission_classes
    assert IsAdminUser in view.permission_classes


@pytest.mark.unit
def test_get_added_visited_countries_by_day_has_correct_http_methods() -> None:
    """Тест что GetAddedVisitedCountriesByDay разрешает только GET"""
    view = GetAddedVisitedCountriesByDay()
    assert view.http_method_names == ['get']


@pytest.mark.unit
def test_all_api_views_inherit_from_list_api_view() -> None:
    """Тест что все API вьюхи наследуются от ListAPIView"""
    from rest_framework import generics

    views = [
        GetTotalVisitedCountries,
        GetUsersWithVisitedCountries,
        GetAverageQtyVisitedCountries,
        GetMaxQtyVisitedCountries,
        GetAddedVisitedCountryYeterday,
        GetAddedVisitedCountriesByDay,
    ]

    for view_class in views:
        assert issubclass(view_class, generics.ListAPIView)


@pytest.mark.unit
def test_get_total_visited_countries_response_structure() -> None:
    """Тест структуры ответа GetTotalVisitedCountries"""
    view = GetTotalVisitedCountries()

    with patch('dashboard.api.VisitedCountry.objects') as mock_objects:
        mock_objects.count.return_value = 42

        request = Mock()
        response = view.get(request)

        assert 'qty' in response.data
        assert response.data['qty'] == 42


@pytest.mark.unit
def test_get_users_with_visited_countries_response_structure() -> None:
    """Тест структуры ответа GetUsersWithVisitedCountries"""
    view = GetUsersWithVisitedCountries()
    view.queryset = Mock()

    with patch.object(view.queryset, 'values') as mock_values:
        mock_distinct = Mock()
        mock_distinct.count.return_value = 15
        mock_values.return_value.distinct.return_value = mock_distinct

        request = Mock()
        response = view.get(request)

        assert 'qty' in response.data
        assert response.data['qty'] == 15


@pytest.mark.unit
def test_get_average_qty_visited_countries_calculates_correctly() -> None:
    """Тест правильности расчета среднего количества стран"""
    view = GetAverageQtyVisitedCountries()
    view.queryset = Mock()

    with patch.object(view.queryset, 'count', return_value=100):
        with patch.object(view.queryset, 'values') as mock_values:
            mock_distinct = Mock()
            mock_distinct.count.return_value = 10
            mock_values.return_value.distinct.return_value = mock_distinct

            request = Mock()
            response = view.get(request)

            # 100 стран / 10 пользователей = 10
            assert response.data['qty'] == 10


@pytest.mark.unit
def test_get_max_qty_visited_countries_response_structure() -> None:
    """Тест структуры ответа GetMaxQtyVisitedCountries"""
    view = GetMaxQtyVisitedCountries()
    view.queryset = Mock()

    with patch.object(view.queryset, 'values') as mock_values:
        mock_annotate = Mock()
        mock_annotate.aggregate.return_value = {'qty': 25}
        mock_values.return_value.annotate.return_value = mock_annotate

        request = Mock()
        response = view.get(request)

        assert 'qty' in response.data
        assert response.data['qty'] == 25


@pytest.mark.unit
def test_get_added_visited_country_yesterday_uses_days_param() -> None:
    """Тест что GetAddedVisitedCountryYeterday использует параметр days"""
    view = GetAddedVisitedCountryYeterday()
    view.queryset = Mock()
    view.kwargs = {'days': 7}

    with patch.object(view.queryset, 'filter') as mock_filter:
        mock_filter.return_value.count.return_value = 5

        request = Mock()
        response = view.get(request)

        assert response.data['qty'] == 5
        mock_filter.assert_called_once()


@pytest.mark.unit
def test_get_added_visited_countries_by_day_response_is_list() -> None:
    """Тест что GetAddedVisitedCountriesByDay возвращает список"""
    view = GetAddedVisitedCountriesByDay()
    view.queryset = Mock()

    mock_data = [
        {'date': '01.01.2024', 'qty': 5},
        {'date': '02.01.2024', 'qty': 3},
    ]

    with patch.object(view.queryset, 'annotate') as mock_annotate:
        mock_annotate.return_value.order_by.return_value.annotate.return_value.values.return_value.annotate.return_value.__getitem__.return_value = mock_data

        request = Mock()
        response = view.get(request)

        assert isinstance(response.data, list)
