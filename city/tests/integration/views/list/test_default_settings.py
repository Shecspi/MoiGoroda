"""
Тесты применения настроек по умолчанию фильтрации и сортировки в списке городов.

Покрывает:
- Применение настроек фильтрации по умолчанию при отсутствии GET-параметров
- Применение настроек сортировки по умолчанию при отсутствии GET-параметров
- Приоритет GET-параметров над настройками по умолчанию
- Передачу настроек по умолчанию в контекст
- Корректное отображение в панели фильтрации

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any
from unittest.mock import patch, MagicMock

import pytest
from django.test import Client
from django.urls import reverse

from city.models import CityListDefaultSettings, VisitedCity


@pytest.fixture
def authenticated_user(client: Client, django_user_model: Any) -> Any:
    """Создает и аутентифицирует пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass123')
    client.login(username='testuser', password='testpass123')
    return user


@pytest.mark.django_db
@patch('city.views.logger')
@patch('city.views.apply_sort_to_queryset')
@patch('city.views.apply_filter_to_queryset')
@patch('city.views.get_unique_visited_cities')
@patch('city.views.get_number_of_cities')
@patch('city.views.get_number_of_new_visited_cities')
@patch('city.views.get_number_of_visited_countries')
@patch('city.views.is_user_has_subscriptions')
@patch('city.views.get_all_subscriptions')
@pytest.mark.integration
class TestDefaultSettingsApplication:
    """Тесты применения настроек по умолчанию."""

    def test_applies_default_filter_when_no_get_parameter(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_filter: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Проверяет применение фильтра по умолчанию при отсутствии GET-параметра."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_filter.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Создаём настройку по умолчанию
        CityListDefaultSettings.objects.create(
            user=authenticated_user,
            parameter_type='filter',
            parameter_value='magnet',
        )

        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        # Проверяем, что фильтр был применён
        mock_apply_filter.assert_called_once()
        call_args = mock_apply_filter.call_args
        assert call_args[0][2] == 'magnet'  # Третий аргумент - значение фильтра
        # Проверяем, что значение передано в контекст
        assert response.context['filter'] == 'magnet'

    def test_applies_default_sort_when_no_get_parameter(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_filter: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Проверяет применение сортировки по умолчанию при отсутствии GET-параметра."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_filter.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Создаём настройку сортировки по умолчанию
        CityListDefaultSettings.objects.create(
            user=authenticated_user,
            parameter_type='sort',
            parameter_value='name_up',
        )

        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        # Проверяем, что сортировка была применена
        mock_apply_sort.assert_called_once()
        # Проверяем, что значение передано в контекст
        assert response.context['sort'] == 'name_up'

    def test_get_parameter_overrides_default_filter(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_filter: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Проверяет, что GET-параметр имеет приоритет над настройкой по умолчанию."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_filter.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Создаём настройку по умолчанию
        CityListDefaultSettings.objects.create(
            user=authenticated_user,
            parameter_type='filter',
            parameter_value='magnet',
        )

        # Запрашиваем с GET-параметром
        response = client.get(reverse('city-all-list') + '?filter=no_magnet')

        assert response.status_code == 200
        # Проверяем, что использован GET-параметр, а не настройка по умолчанию
        call_args = mock_apply_filter.call_args
        assert call_args[0][2] == 'no_magnet'
        assert response.context['filter'] == 'no_magnet'

    def test_get_parameter_overrides_default_sort(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_filter: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Проверяет, что GET-параметр имеет приоритет над настройкой сортировки по умолчанию."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_filter.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Создаём настройку сортировки по умолчанию
        CityListDefaultSettings.objects.create(
            user=authenticated_user,
            parameter_type='sort',
            parameter_value='name_up',
        )

        # Запрашиваем с GET-параметром
        response = client.get(reverse('city-all-list') + '?sort=last_visit_date_down')

        assert response.status_code == 200
        # Проверяем, что использован GET-параметр
        assert response.context['sort'] == 'last_visit_date_down'

    def test_default_settings_passed_to_context(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_filter: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Проверяет передачу настроек по умолчанию в контекст."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_filter.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Создаём настройки по умолчанию
        CityListDefaultSettings.objects.create(
            user=authenticated_user,
            parameter_type='filter',
            parameter_value='current_year',
        )
        CityListDefaultSettings.objects.create(
            user=authenticated_user,
            parameter_type='sort',
            parameter_value='name_down',
        )

        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        assert response.context['default_filter'] == 'current_year'
        assert response.context['default_sort'] == 'name_down'

    def test_no_default_settings_when_none_exist(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_filter: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Проверяет поведение при отсутствии настроек по умолчанию."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_filter.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        assert response.context['default_filter'] is None
        assert response.context['default_sort'] is None
        # Проверяем, что используется стандартная сортировка
        assert response.context['sort'] == 'last_visit_date_down'

    def test_applies_both_default_filter_and_sort(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_filter: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Проверяет одновременное применение фильтра и сортировки по умолчанию."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_filter.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Создаём обе настройки по умолчанию
        CityListDefaultSettings.objects.create(
            user=authenticated_user,
            parameter_type='filter',
            parameter_value='last_year',
        )
        CityListDefaultSettings.objects.create(
            user=authenticated_user,
            parameter_type='sort',
            parameter_value='first_visit_date_up',
        )

        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        # Проверяем применение фильтра
        call_args = mock_apply_filter.call_args
        assert call_args[0][2] == 'last_year'
        assert response.context['filter'] == 'last_year'
        # Проверяем применение сортировки
        assert response.context['sort'] == 'first_visit_date_up'
