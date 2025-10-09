"""
Тесты данных контекста страницы карты городов.
Проверяет корректность передаваемых данных.

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
@patch('city.views.logger')
@patch('city.views.get_number_of_cities')
@patch('city.views.get_number_of_new_visited_cities')
@patch('city.views.get_number_of_visited_countries')
@patch('city.views.is_user_has_subscriptions')
@patch('city.views.get_all_subscriptions')
class TestStatisticsContext:
    """Тесты статистических данных в контексте."""

    def test_statistics_values_correct(
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
        """Статистические значения передаются корректно."""
        mock_get_number_of_cities.return_value = 150
        mock_get_number_of_new_visited_cities.return_value = 42
        mock_get_number_of_visited_countries.return_value = 5
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-map'))

        assert response.context['total_qty_of_cities'] == 150
        assert response.context['qty_of_visited_cities'] == 42
        assert response.context['number_of_visited_countries'] == 5

    def test_country_statistics_without_country_param(
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
        """Статистика по стране без параметра country."""
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 10
        mock_get_number_of_visited_countries.return_value = 3
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-map'))

        # Без country параметра статистика по стране должна быть 0 или равна общей
        assert 'number_of_cities_in_country' in response.context
        assert 'number_of_visited_cities_in_country' in response.context

    @patch('city.views.Country.objects.get')
    def test_country_statistics_with_country_param(
        self,
        mock_country_get: MagicMock,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Статистика по стране с параметром country."""
        with patch('city.views.Country.objects.filter') as mock_country_filter:
            mock_country_filter.return_value.exists.return_value = True
            mock_country_get.return_value = Mock(__str__=lambda x: 'Россия')

            # Первый вызов - для всех городов, второй - для городов в стране
            mock_get_number_of_cities.side_effect = [1000, 200]
            mock_get_number_of_new_visited_cities.side_effect = [100, 25]
            mock_get_number_of_visited_countries.return_value = 5
            mock_is_user_has_subscriptions.return_value = False
            mock_get_all_subscriptions.return_value = []

            response = client.get(reverse('city-all-map') + '?country=RU')

            assert response.context['total_qty_of_cities'] == 1000
            assert response.context['number_of_cities_in_country'] == 200
            assert response.context['qty_of_visited_cities'] == 100
            assert response.context['number_of_visited_cities_in_country'] == 25

    def test_subscriptions_data_included(
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
        """Данные о подписках включены в контекст."""
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 10
        mock_get_number_of_visited_countries.return_value = 3

        mock_subscriptions = [Mock(id=1), Mock(id=2)]
        mock_is_user_has_subscriptions.return_value = True
        mock_get_all_subscriptions.return_value = mock_subscriptions

        response = client.get(reverse('city-all-map'))

        assert response.context['is_user_has_subscriptions'] is True
        assert response.context['subscriptions'] == mock_subscriptions
        assert len(response.context['subscriptions']) == 2


@pytest.mark.django_db
@patch('city.views.logger')
@patch('city.views.get_number_of_cities')
@patch('city.views.get_number_of_new_visited_cities')
@patch('city.views.get_number_of_visited_countries')
@patch('city.views.is_user_has_subscriptions')
@patch('city.views.get_all_subscriptions')
class TestActivePageMarker:
    """Тесты маркера активной страницы."""

    def test_active_page_is_city_map(
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
        """Маркер активной страницы установлен на 'city_map'."""
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-map'))

        assert response.context['active_page'] == 'city_map'


@pytest.mark.django_db
@patch('city.views.logger')
@patch('city.views.get_number_of_cities')
@patch('city.views.get_number_of_new_visited_cities')
@patch('city.views.get_number_of_visited_countries')
@patch('city.views.is_user_has_subscriptions')
@patch('city.views.get_all_subscriptions')
class TestPageTitles:
    """Тесты заголовков страницы."""

    def test_default_page_title(
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
        """Заголовок по умолчанию отображается корректно."""
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-map'))

        assert response.context['page_title'] == 'Карта посещённых городов'
        assert response.context['page_description'] == 'Карта с отмеченными посещёнными городами'

    @patch('city.views.Country.objects.filter')
    @patch('city.views.Country.objects.get')
    @patch('city.views.to_prepositional')
    def test_country_specific_page_title(
        self,
        mock_to_prepositional: MagicMock,
        mock_country_get: MagicMock,
        mock_country_filter: MagicMock,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Заголовок для конкретной страны формируется корректно."""
        mock_country_filter.return_value.exists.return_value = True
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        mock_country_get.return_value = Mock(__str__=lambda x: 'Россия')
        mock_to_prepositional.return_value = 'России'

        response = client.get(reverse('city-all-map') + '?country=RU')

        assert 'Карта посещённых городов в России' in response.context['page_title']
        mock_to_prepositional.assert_called_once_with('Россия')
