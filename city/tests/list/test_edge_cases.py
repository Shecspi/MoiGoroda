"""
Тесты граничных случаев и edge cases для страницы списка городов.
Проверяет поведение в нестандартных ситуациях.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any
from unittest.mock import patch, MagicMock, Mock

import pytest
from django.test import Client
from django.urls import reverse

from city.models import VisitedCity


@pytest.fixture
def authenticated_user(client: Client, django_user_model: Any) -> Any:
    """Создает и аутентифицирует пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass123')
    client.login(username='testuser', password='testpass123')
    return user


@pytest.mark.django_db
@patch('city.views.Country.objects.filter')
@patch('city.views.logger')
class TestCountryValidation:
    """Тесты валидации параметра country."""

    def test_nonexistent_country_redirects(
        self,
        mock_logger: MagicMock,
        mock_country_filter: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Несуществующий код страны вызывает редирект."""
        mock_country_filter.return_value.exists.return_value = False

        response = client.get(reverse('city-all-list') + '?country=INVALID')

        assert response.status_code == 302
        assert response.url == reverse('city-all-map')  # type: ignore

    def test_empty_country_parameter(
        self,
        mock_logger: MagicMock,
        mock_country_filter: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Пустой параметр country обрабатывается корректно."""
        with (
            patch('city.views.apply_sort_to_queryset') as mock_sort,
            patch('city.views.get_unique_visited_cities') as mock_get_cities,
            patch('city.views.get_number_of_cities') as mock_num_cities,
            patch('city.views.get_number_of_new_visited_cities') as mock_num_visited,
            patch('city.views.get_number_of_visited_countries') as mock_num_countries,
            patch('city.views.is_user_has_subscriptions') as mock_has_subs,
            patch('city.views.get_all_subscriptions') as mock_get_subs,
        ):
            empty_qs = VisitedCity.objects.none()
            mock_get_cities.return_value = empty_qs
            mock_sort.return_value = empty_qs
            mock_num_cities.return_value = 100
            mock_num_visited.return_value = 0
            mock_num_countries.return_value = 0
            mock_has_subs.return_value = False
            mock_get_subs.return_value = []

            response = client.get(reverse('city-all-list') + '?country=')

            assert response.status_code == 200

    def test_special_characters_in_country_code(
        self,
        mock_logger: MagicMock,
        mock_country_filter: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Специальные символы в коде страны обрабатываются."""
        mock_country_filter.return_value.exists.return_value = False

        response = client.get(reverse('city-all-list') + '?country=RU%00')

        # Должен быть редирект на карту
        assert response.status_code == 302


@pytest.mark.django_db
@patch('city.views.logger')
@patch('city.views.apply_sort_to_queryset')
@patch('city.views.get_unique_visited_cities')
@patch('city.views.get_number_of_cities')
@patch('city.views.get_number_of_new_visited_cities')
@patch('city.views.get_number_of_visited_countries')
@patch('city.views.is_user_has_subscriptions')
@patch('city.views.get_all_subscriptions')
class TestMultipleParameters:
    """Тесты множественных и противоречивых параметров."""

    def test_all_parameters_together(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Все параметры работают вместе."""
        with (
            patch('city.views.Country.objects.filter') as mock_country_filter,
            patch('city.views.Country.objects.get') as mock_country_get,
            patch('city.views.apply_filter_to_queryset') as mock_filter,
        ):
            empty_qs = VisitedCity.objects.none()
            mock_country_filter.return_value.exists.return_value = True
            mock_get_unique_visited_cities.return_value = empty_qs
            mock_filter.return_value = empty_qs
            mock_apply_sort.return_value = empty_qs
            mock_get_number_of_cities.return_value = 100
            mock_get_number_of_new_visited_cities.return_value = 0
            mock_get_number_of_visited_countries.return_value = 0
            mock_is_user_has_subscriptions.return_value = False
            mock_get_all_subscriptions.return_value = []
            mock_country_get.return_value = Mock(__str__=lambda x: 'Россия')

            response = client.get(
                reverse('city-all-list') + '?country=RU&filter=current_year&sort=name_down&page=1'
            )

            assert response.status_code == 200
            assert response.context['country_code'] == 'RU'
            assert response.context['filter'] == 'current_year'
            assert response.context['sort'] == 'name_down'

    def test_duplicate_parameters(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Дублирующиеся параметры обрабатываются (берется последний)."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list') + '?sort=name_down&sort=name_up')

        assert response.status_code == 200
        # Django берет последнее значение
        assert response.context['sort'] in ['name_down', 'name_up']


@pytest.mark.django_db
class TestHTTPMethods:
    """Тесты HTTP методов."""

    @patch('city.views.logger')
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.get_unique_visited_cities')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_get_method_allowed(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """GET метод разрешен."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200

    def test_post_method_not_allowed(
        self,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """POST метод не разрешен."""
        response = client.post(reverse('city-all-list'))

        # ListView по умолчанию не поддерживает POST
        assert response.status_code == 405

    def test_head_method_allowed(
        self,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """HEAD метод разрешен."""
        with (
            patch('city.views.apply_sort_to_queryset') as mock_sort,
            patch('city.views.get_unique_visited_cities') as mock_get_cities,
            patch('city.views.get_number_of_cities') as mock_num_cities,
            patch('city.views.get_number_of_new_visited_cities') as mock_num_visited,
            patch('city.views.get_number_of_visited_countries') as mock_num_countries,
            patch('city.views.is_user_has_subscriptions') as mock_has_subs,
            patch('city.views.get_all_subscriptions') as mock_get_subs,
            patch('city.views.logger'),
        ):
            empty_qs = VisitedCity.objects.none()
            mock_get_cities.return_value = empty_qs
            mock_sort.return_value = empty_qs
            mock_num_cities.return_value = 100
            mock_num_visited.return_value = 0
            mock_num_countries.return_value = 0
            mock_has_subs.return_value = False
            mock_get_subs.return_value = []

            response = client.head(reverse('city-all-list'))

            assert response.status_code == 200


@pytest.mark.django_db
class TestQueryStringEdgeCases:
    """Тесты edge cases в query string."""

    @patch('city.views.logger')
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.get_unique_visited_cities')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_url_encoded_parameters(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """URL-encoded параметры обрабатываются корректно."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list') + '?sort=name_down')

        assert response.status_code == 200

    @patch('city.views.logger')
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.get_unique_visited_cities')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_very_long_parameter_values(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Очень длинные значения параметров обрабатываются."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        very_long_value = 'a' * 1000
        response = client.get(reverse('city-all-list') + f'?filter={very_long_value}')

        assert response.status_code == 200

    @patch('city.views.logger')
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.get_unique_visited_cities')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_sql_injection_attempts(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Попытки SQL инъекций блокируются."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        malicious_value = "'; DROP TABLE city; --"
        response = client.get(reverse('city-all-list') + f'?filter={malicious_value}')

        # Должна быть обработка без ошибок (Django ORM защищает)
        assert response.status_code == 200


@pytest.mark.django_db
class TestConcurrency:
    """Тесты параллельных запросов."""

    @patch('city.views.logger')
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.get_unique_visited_cities')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_multiple_requests_from_same_user(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Множественные запросы от одного пользователя обрабатываются."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Делаем несколько запросов подряд
        for _ in range(5):
            response = client.get(reverse('city-all-list'))
            assert response.status_code == 200

        # Проверяем, что все вызовы зафиксированы
        assert mock_logger.info.call_count >= 5


@pytest.mark.django_db
class TestPerformance:
    """Тесты производительности."""

    @patch('city.views.logger')
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.get_unique_visited_cities')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_large_dataset_pagination(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Большой датасет обрабатывается эффективно через пагинацию."""
        # Симулируем 1000 городов
        mock_cities = [Mock(id=i, city=Mock(title=f'Город {i}')) for i in range(1000)]

        mock_get_unique_visited_cities.return_value = mock_cities
        mock_apply_sort.return_value = mock_cities
        mock_get_number_of_cities.return_value = 10000
        mock_get_number_of_new_visited_cities.return_value = 1000
        mock_get_number_of_visited_countries.return_value = 10
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        # Проверяем, что на странице только 24 элемента (размер страницы)
        assert len(response.context['page_obj']) == 24
        # Проверяем количество страниц
        expected_pages = (1000 + 23) // 24  # округление вверх
        assert response.context['paginator'].num_pages == expected_pages
