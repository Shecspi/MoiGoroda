"""
Тесты параметра country для страницы карты городов.
Проверяет валидацию и обработку кода страны.

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
class TestCountryValidation:
    """Тесты валидации параметра country."""

    @patch('city.views.Country.objects.filter')
    @patch('city.views.logger')
    def test_invalid_country_redirects(
        self,
        mock_logger: MagicMock,
        mock_country_filter: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Несуществующий код страны вызывает редирект на карту без параметров."""
        mock_country_filter.return_value.exists.return_value = False

        response = client.get(reverse('city-all-map') + '?country=INVALID')

        assert response.status_code == 302
        assert response.url == reverse('city-all-map')  # type: ignore

    @patch('city.views.Country.objects.filter')
    @patch('city.views.Country.objects.get')
    @patch('city.views.logger')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_valid_country_loads_successfully(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_logger: MagicMock,
        mock_country_get: MagicMock,
        mock_country_filter: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Валидный код страны обрабатывается корректно."""
        mock_country_filter.return_value.exists.return_value = True
        mock_country_get.return_value = Mock(__str__=lambda x: 'Россия')
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 10
        mock_get_number_of_visited_countries.return_value = 3
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-map') + '?country=RU')

        assert response.status_code == 200
        assert response.context['country_name'] == 'Россия'
        assert response.context['country_code'] == 'RU'

    @patch('city.views.logger')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_without_country_parameter(
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
        """Страница работает без параметра country."""
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 10
        mock_get_number_of_visited_countries.return_value = 3
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-map'))

        assert response.status_code == 200
        assert response.context['country_code'] is None
        assert response.context['country_name'] == ''

    @patch('city.views.Country.objects.filter')
    @patch('city.views.logger')
    def test_empty_country_parameter(
        self,
        mock_logger: MagicMock,
        mock_country_filter: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Пустой параметр country обрабатывается как отсутствие параметра."""
        with (
            patch('city.views.get_number_of_cities') as mock_num_cities,
            patch('city.views.get_number_of_new_visited_cities') as mock_num_visited,
            patch('city.views.get_number_of_visited_countries') as mock_num_countries,
            patch('city.views.is_user_has_subscriptions') as mock_has_subs,
            patch('city.views.get_all_subscriptions') as mock_get_subs,
        ):
            mock_num_cities.return_value = 100
            mock_num_visited.return_value = 0
            mock_num_countries.return_value = 0
            mock_has_subs.return_value = False
            mock_get_subs.return_value = []

            response = client.get(reverse('city-all-map') + '?country=')

            assert response.status_code == 200


@pytest.mark.django_db
@patch('city.views.Country.objects.filter')
@patch('city.views.logger')
class TestCountryEdgeCases:
    """Тесты граничных случаев для параметра country."""

    def test_special_characters_in_country_code(
        self,
        mock_logger: MagicMock,
        mock_country_filter: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Специальные символы в коде страны обрабатываются."""
        mock_country_filter.return_value.exists.return_value = False

        response = client.get(reverse('city-all-map') + '?country=RU%00')

        assert response.status_code == 302
        assert response.url == reverse('city-all-map')  # type: ignore

    def test_very_long_country_code(
        self,
        mock_logger: MagicMock,
        mock_country_filter: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Очень длинный код страны обрабатывается."""
        mock_country_filter.return_value.exists.return_value = False

        very_long_code = 'A' * 100
        response = client.get(reverse('city-all-map') + f'?country={very_long_code}')

        assert response.status_code == 302

    def test_lowercase_country_code(
        self,
        mock_logger: MagicMock,
        mock_country_filter: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Код страны в нижнем регистре обрабатывается."""
        with (
            patch('city.views.Country.objects.get') as mock_country_get,
            patch('city.views.get_number_of_cities') as mock_num_cities,
            patch('city.views.get_number_of_new_visited_cities') as mock_num_visited,
            patch('city.views.get_number_of_visited_countries') as mock_num_countries,
            patch('city.views.is_user_has_subscriptions') as mock_has_subs,
            patch('city.views.get_all_subscriptions') as mock_get_subs,
        ):
            mock_country_filter.return_value.exists.return_value = True
            mock_country_get.return_value = Mock(__str__=lambda x: 'Россия')
            mock_num_cities.return_value = 100
            mock_num_visited.return_value = 0
            mock_num_countries.return_value = 0
            mock_has_subs.return_value = False
            mock_get_subs.return_value = []

            response = client.get(reverse('city-all-map') + '?country=ru')

            assert response.status_code == 200
            assert response.context['country_code'] == 'ru'

    def test_numeric_country_code(
        self,
        mock_logger: MagicMock,
        mock_country_filter: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Числовой код страны обрабатывается."""
        mock_country_filter.return_value.exists.return_value = False

        response = client.get(reverse('city-all-map') + '?country=123')

        assert response.status_code == 302
