"""
Unit-тесты для отдельных методов VisitedCity_List view.
Тестируют изолированные компоненты без полного HTTP flow.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from unittest.mock import Mock, patch, MagicMock

import pytest
from django.http import HttpRequest
from django.test import RequestFactory

from city.models import VisitedCity
from city.views import VisitedCity_List


@pytest.fixture
def mock_request() -> HttpRequest:
    """Создает mock HTTP request."""
    factory = RequestFactory()
    request = factory.get('/city/all/list')
    request.user = Mock(pk=1, id=1, is_authenticated=True)
    return request


@pytest.fixture
def view_instance() -> VisitedCity_List:
    """Создает экземпляр view."""
    return VisitedCity_List()


@pytest.mark.unit
class TestGetQueryset:
    """Тестирует метод get_queryset."""

    @pytest.mark.django_db
    @patch('city.views.get_unique_visited_cities')
    @patch('city.views.apply_filter_to_queryset')
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.logger')
    def test_get_queryset_without_filters(
        self,
        mock_logger: MagicMock,
        mock_apply_sort: MagicMock,
        mock_apply_filter: MagicMock,
        mock_get_cities: MagicMock,
        view_instance: VisitedCity_List,
        mock_request: HttpRequest,
    ) -> None:
        """Проверяет получение queryset без фильтров и кода страны."""
        empty_qs = VisitedCity.objects.none()
        mock_get_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs

        view_instance.request = mock_request
        result = view_instance.get_queryset()

        assert result == empty_qs
        mock_get_cities.assert_called_once_with(1, None)
        mock_apply_filter.assert_not_called()
        mock_apply_sort.assert_called_once()
        mock_logger.info.assert_called_once()

    @pytest.mark.django_db
    @patch('city.views.Country.objects.get')
    @patch('city.views.get_unique_visited_cities')
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.logger')
    def test_get_queryset_with_country_code(
        self,
        mock_logger: MagicMock,
        mock_apply_sort: MagicMock,
        mock_get_cities: MagicMock,
        mock_country_get: MagicMock,
        view_instance: VisitedCity_List,
    ) -> None:
        """Проверяет получение queryset с кодом страны."""
        factory = RequestFactory()
        request = factory.get('/city/all/list?country=RU')
        request.user = Mock(pk=1)

        empty_qs = VisitedCity.objects.none()
        mock_get_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_country_get.return_value = Mock(__str__=lambda x: 'Россия')

        view_instance.request = request
        result = view_instance.get_queryset()

        assert result == empty_qs
        mock_get_cities.assert_called_once_with(1, 'RU')
        assert view_instance.country == 'Россия'
        assert view_instance.country_code == 'RU'


@pytest.mark.unit
class TestApplyFilter:
    """Тестирует метод apply_filter."""

    @pytest.mark.django_db
    @patch('city.views.apply_filter_to_queryset')
    @patch('city.views.logger')
    def test_apply_filter_with_valid_filter(
        self,
        mock_logger: MagicMock,
        mock_apply_filter: MagicMock,
        view_instance: VisitedCity_List,
        mock_request: HttpRequest,
    ) -> None:
        """Проверяет применение валидного фильтра."""
        empty_qs = VisitedCity.objects.none()
        filtered_qs = VisitedCity.objects.none()
        mock_apply_filter.return_value = filtered_qs

        view_instance.request = mock_request
        view_instance.queryset = empty_qs
        view_instance.filter = 'current_year'
        view_instance.user_id = 1

        view_instance.apply_filter()

        mock_apply_filter.assert_called_once_with(empty_qs, 1, 'current_year')
        assert view_instance.queryset == filtered_qs
        mock_logger.warning.assert_not_called()

    @pytest.mark.django_db
    @patch('city.views.apply_filter_to_queryset')
    @patch('city.views.logger')
    def test_apply_filter_with_invalid_filter(
        self,
        mock_logger: MagicMock,
        mock_apply_filter: MagicMock,
        view_instance: VisitedCity_List,
        mock_request: HttpRequest,
    ) -> None:
        """Проверяет обработку некорректного фильтра."""
        empty_qs = VisitedCity.objects.none()
        mock_apply_filter.side_effect = KeyError('Invalid filter')

        view_instance.request = mock_request
        view_instance.queryset = empty_qs
        view_instance.filter = 'invalid_filter'
        view_instance.user_id = 1

        view_instance.apply_filter()

        mock_logger.warning.assert_called_once()
        # Queryset не должен измениться
        assert view_instance.queryset == empty_qs

    @pytest.mark.unit
    @pytest.mark.django_db
    def test_apply_filter_without_filter_param(
        self,
        view_instance: VisitedCity_List,
        mock_request: HttpRequest,
    ) -> None:
        """Проверяет, что без параметра filter метод ничего не делает."""
        empty_qs = VisitedCity.objects.none()

        view_instance.request = mock_request
        view_instance.queryset = empty_qs
        view_instance.filter = None

        view_instance.apply_filter()

        # Queryset не должен измениться
        assert view_instance.queryset == empty_qs


@pytest.mark.unit
class TestApplySort:
    """Тестирует метод apply_sort."""

    @pytest.mark.django_db
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.logger')
    def test_apply_sort_with_valid_sort(
        self,
        mock_logger: MagicMock,
        mock_apply_sort: MagicMock,
        view_instance: VisitedCity_List,
    ) -> None:
        """Проверяет применение валидной сортировки."""
        factory = RequestFactory()
        request = factory.get('/city/all/list?sort=name_down')
        request.user = Mock(pk=1)

        empty_qs = VisitedCity.objects.none()
        sorted_qs = VisitedCity.objects.none()
        mock_apply_sort.return_value = sorted_qs

        view_instance.request = request
        view_instance.queryset = empty_qs

        view_instance.apply_sort(default_sort=None)

        mock_apply_sort.assert_called_once_with(empty_qs, 'name_down')
        assert view_instance.queryset == sorted_qs
        assert view_instance.sort == 'name_down'

    @pytest.mark.django_db
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.logger')
    def test_apply_sort_with_default_sort(
        self,
        mock_logger: MagicMock,
        mock_apply_sort: MagicMock,
        view_instance: VisitedCity_List,
        mock_request: HttpRequest,
    ) -> None:
        """Проверяет применение сортировки по умолчанию."""
        empty_qs = VisitedCity.objects.none()
        sorted_qs = VisitedCity.objects.none()
        mock_apply_sort.return_value = sorted_qs

        view_instance.request = mock_request
        view_instance.queryset = empty_qs

        view_instance.apply_sort(default_sort=None)

        mock_apply_sort.assert_called_once_with(empty_qs, 'last_visit_date_down')
        assert view_instance.sort == 'last_visit_date_down'

    @pytest.mark.django_db
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.logger')
    def test_apply_sort_with_invalid_sort(
        self,
        mock_logger: MagicMock,
        mock_apply_sort: MagicMock,
        view_instance: VisitedCity_List,
    ) -> None:
        """Проверяет обработку некорректной сортировки."""
        factory = RequestFactory()
        request = factory.get('/city/all/list?sort=invalid')
        request.user = Mock(pk=1)

        empty_qs = VisitedCity.objects.none()
        # При некорректной сортировке выбрасывается KeyError
        mock_apply_sort.side_effect = KeyError('Invalid sort')

        view_instance.request = request
        view_instance.queryset = empty_qs

        view_instance.apply_sort(default_sort=None)

        # Должна быть только одна попытка - с 'invalid'
        # После чего обрабатывается исключение и sort устанавливается в default
        assert mock_apply_sort.call_count == 1
        mock_logger.warning.assert_called_once()
        assert view_instance.sort == 'last_visit_date_down'

    @pytest.mark.django_db
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.logger')
    def test_apply_sort_with_saved_default_sort(
        self,
        mock_logger: MagicMock,
        mock_apply_sort: MagicMock,
        view_instance: VisitedCity_List,
        mock_request: HttpRequest,
    ) -> None:
        """Проверяет применение сохранённой сортировки по умолчанию."""
        empty_qs = VisitedCity.objects.none()
        sorted_qs = VisitedCity.objects.none()
        mock_apply_sort.return_value = sorted_qs

        view_instance.request = mock_request
        view_instance.queryset = empty_qs

        # Передаём сохранённую сортировку по умолчанию
        view_instance.apply_sort(default_sort='name_up')

        mock_apply_sort.assert_called_once_with(empty_qs, 'name_up')
        assert view_instance.sort == 'name_up'
