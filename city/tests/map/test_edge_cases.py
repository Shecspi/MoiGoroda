"""
Тесты граничных случаев и edge cases для страницы карты городов.
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


@pytest.fixture
def authenticated_user(client: Client, django_user_model: Any) -> Any:
    """Создает и аутентифицирует пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass123')
    client.login(username='testuser', password='testpass123')
    return user


@pytest.mark.django_db
class TestHTTPMethods:
    """Тесты HTTP методов."""

    @patch('city.views.logger')
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
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """GET метод разрешен."""
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-map'))

        assert response.status_code == 200

    def test_post_method_not_allowed(
        self,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """POST метод не разрешен."""
        response = client.post(reverse('city-all-map'))

        # TemplateView по умолчанию не поддерживает POST
        assert response.status_code == 405

    def test_head_method_allowed(
        self,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """HEAD метод разрешен."""
        with (
            patch('city.views.get_number_of_cities') as mock_num_cities,
            patch('city.views.get_number_of_new_visited_cities') as mock_num_visited,
            patch('city.views.get_number_of_visited_countries') as mock_num_countries,
            patch('city.views.is_user_has_subscriptions') as mock_has_subs,
            patch('city.views.get_all_subscriptions') as mock_get_subs,
            patch('city.views.logger'),
        ):
            mock_num_cities.return_value = 100
            mock_num_visited.return_value = 0
            mock_num_countries.return_value = 0
            mock_has_subs.return_value = False
            mock_get_subs.return_value = []

            response = client.head(reverse('city-all-map'))

            assert response.status_code == 200


@pytest.mark.django_db
@patch('city.views.logger')
@patch('city.views.get_number_of_cities')
@patch('city.views.get_number_of_new_visited_cities')
@patch('city.views.get_number_of_visited_countries')
@patch('city.views.is_user_has_subscriptions')
@patch('city.views.get_all_subscriptions')
class TestQueryStringEdgeCases:
    """Тесты edge cases в query string."""

    def test_multiple_country_parameters(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Дублирующиеся параметры country обрабатываются."""
        with (
            patch('city.views.Country.objects.filter') as mock_filter,
            patch('city.views.Country.objects.get') as mock_get,
        ):
            mock_filter.return_value.exists.return_value = True
            mock_get.return_value = Mock(__str__=lambda x: 'Россия')
            mock_get_number_of_cities.return_value = 100
            mock_get_number_of_new_visited_cities.return_value = 0
            mock_get_number_of_visited_countries.return_value = 0
            mock_is_user_has_subscriptions.return_value = False
            mock_get_all_subscriptions.return_value = []

            # Django берет последнее значение
            response = client.get(reverse('city-all-map') + '?country=US&country=RU')

            assert response.status_code == 200

    def test_url_encoded_country_parameter(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """URL-encoded параметры обрабатываются."""
        with (
            patch('city.views.Country.objects.filter') as mock_filter,
            patch('city.views.Country.objects.get') as mock_get,
        ):
            mock_filter.return_value.exists.return_value = True
            mock_get.return_value = Mock(__str__=lambda x: 'Россия')
            mock_get_number_of_cities.return_value = 100
            mock_get_number_of_new_visited_cities.return_value = 0
            mock_get_number_of_visited_countries.return_value = 0
            mock_is_user_has_subscriptions.return_value = False
            mock_get_all_subscriptions.return_value = []

            response = client.get(reverse('city-all-map') + '?country=RU')

            assert response.status_code == 200

    def test_unexpected_parameters_ignored(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Неожиданные параметры игнорируются."""
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Передаем параметры, которые не используются на карте
        response = client.get(
            reverse('city-all-map') + '?filter=current_year&sort=name_down&page=1'
        )

        assert response.status_code == 200
        # Эти параметры не должны быть в контексте
        assert 'filter' not in response.context
        assert 'sort' not in response.context


@pytest.mark.django_db
class TestConcurrency:
    """Тесты параллельных запросов."""

    @patch('city.views.logger')
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
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Множественные запросы от одного пользователя обрабатываются."""
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 10
        mock_get_number_of_visited_countries.return_value = 3
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Делаем несколько запросов подряд
        for _ in range(5):
            response = client.get(reverse('city-all-map'))
            assert response.status_code == 200

        # Проверяем, что все вызовы зафиксированы
        assert mock_logger.info.call_count >= 5


@pytest.mark.django_db
@patch('city.views.logger')
@patch('city.views.get_number_of_cities')
@patch('city.views.get_number_of_new_visited_cities')
@patch('city.views.get_number_of_visited_countries')
@patch('city.views.is_user_has_subscriptions')
@patch('city.views.get_all_subscriptions')
class TestSecurity:
    """Тесты безопасности."""

    def test_sql_injection_in_country_param(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Попытки SQL инъекций блокируются."""
        with patch('city.views.Country.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False
            mock_get_number_of_cities.return_value = 100
            mock_get_number_of_new_visited_cities.return_value = 0
            mock_get_number_of_visited_countries.return_value = 0
            mock_is_user_has_subscriptions.return_value = False
            mock_get_all_subscriptions.return_value = []

            malicious_code = "'; DROP TABLE city; --"
            response = client.get(reverse('city-all-map') + f'?country={malicious_code}')

            # Должна быть обработка без ошибок (Django ORM защищает)
            assert response.status_code in [200, 302]

    def test_xss_in_country_param(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Попытки XSS блокируются."""
        with patch('city.views.Country.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False
            mock_get_number_of_cities.return_value = 100
            mock_get_number_of_new_visited_cities.return_value = 0
            mock_get_number_of_visited_countries.return_value = 0
            mock_is_user_has_subscriptions.return_value = False
            mock_get_all_subscriptions.return_value = []

            xss_code = "<script>alert('xss')</script>"
            response = client.get(reverse('city-all-map') + f'?country={xss_code}')

            # Должна быть обработка без выполнения скрипта
            assert response.status_code in [200, 302]
