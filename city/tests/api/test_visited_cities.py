"""
Тесты для эндпоинта /api/city/visited (GetVisitedCities).

Покрывает:
- Получение списка посещенных городов
- Фильтрацию по стране
- Применение дополнительных фильтров
- Проверку авторизации
- Проверку запрещенных HTTP методов

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from unittest.mock import MagicMock, patch
import pytest
from rest_framework import status
from django.urls import reverse

# Фикстуры импортируются автоматически из conftest.py


class TestGetVisitedCities:
    """Тесты для эндпоинта /api/city/visited (GetVisitedCities)."""
    
    url = reverse('api__get_visited_cities')

    def test_guest_cannot_access(self, api_client):
        """Проверяет, что неавторизованные пользователи не могут получить доступ к эндпоинту."""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
    def test_prohibited_methods(self, api_client, authenticated_user, method):
        """Проверяет, что запрещенные HTTP методы возвращают 405."""
        client_method = getattr(api_client, method)
        response = client_method(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @patch('city.api.apply_filter_to_queryset')
    @patch('city.api.get_unique_visited_cities')
    @patch('city.api.logger')
    def test_get_visited_cities_success(
        self, mock_logger, mock_get_unique_visited_cities, mock_apply_filter,
        api_client, authenticated_user, mock_visited_city
    ):
        """Тест успешного получения списка посещенных городов с проверкой логирования."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__.return_value = [mock_visited_city]
        mock_get_unique_visited_cities.return_value = mock_queryset
        
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        mock_logger.info.assert_called_once()
        mock_get_unique_visited_cities.assert_called_once_with(authenticated_user.pk, None)

    @patch('city.api.get_unique_visited_cities')
    def test_get_visited_cities_with_country_filter(
        self, mock_get_unique_visited_cities, api_client, authenticated_user
    ):
        """Тест получения посещенных городов с фильтрацией по стране."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__.return_value = []
        mock_get_unique_visited_cities.return_value = mock_queryset
        
        response = api_client.get(f'{self.url}?country=1')
        
        assert response.status_code == status.HTTP_200_OK
        mock_get_unique_visited_cities.assert_called_once_with(authenticated_user.pk, '1')

    @patch('city.api.apply_filter_to_queryset')
    @patch('city.api.get_unique_visited_cities')
    def test_get_visited_cities_with_filter(
        self, mock_get_unique_visited_cities, mock_apply_filter,
        api_client, authenticated_user
    ):
        """Тест получения посещенных городов с применением дополнительного фильтра."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__.return_value = []
        mock_get_unique_visited_cities.return_value = mock_queryset
        mock_apply_filter.return_value = mock_queryset
        
        response = api_client.get(f'{self.url}?filter=rating_high')
        
        assert response.status_code == status.HTTP_200_OK
        mock_apply_filter.assert_called_once_with(mock_queryset, authenticated_user.pk, 'rating_high')
