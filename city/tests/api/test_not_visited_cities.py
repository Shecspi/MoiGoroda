"""
Тесты для эндпоинта /api/city/not_visited (GetNotVisitedCities).

Покрывает:
- Получение списка непосещенных городов
- Фильтрацию по коду страны
- Проверку авторизации

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


class TestGetNotVisitedCities:
    """Тесты для эндпоинта /api/city/not_visited (GetNotVisitedCities)."""
    
    url = reverse('api__get_not_visited_cities')

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

    @patch('city.api.get_not_visited_cities')
    @patch('city.api.logger')
    def test_get_not_visited_cities_success(
        self, mock_logger, mock_get_not_visited_cities, 
        api_client, authenticated_user, mock_city
    ):
        """Тест успешного получения списка непосещенных городов."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__.return_value = [mock_city]
        mock_get_not_visited_cities.return_value = mock_queryset
        
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        mock_logger.info.assert_called_once()
        mock_get_not_visited_cities.assert_called_once_with(authenticated_user.pk, None)

    @patch('city.api.get_not_visited_cities')
    def test_get_not_visited_cities_with_country(
        self, mock_get_not_visited_cities, api_client, authenticated_user
    ):
        """Тест получения непосещенных городов с фильтрацией по стране."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__.return_value = []
        mock_get_not_visited_cities.return_value = mock_queryset
        
        response = api_client.get(f'{self.url}?country=RU')
        
        assert response.status_code == status.HTTP_200_OK
        mock_get_not_visited_cities.assert_called_once_with(authenticated_user.pk, 'RU')
