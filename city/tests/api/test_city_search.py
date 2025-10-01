"""
Тесты для эндпоинта /api/city/search (city_search).

Покрывает:
- Поиск городов по подстроке в названии
- Валидацию обязательного параметра query
- Дополнительную фильтрацию по коду страны
- Обработку пустых результатов поиска

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


class TestCitySearch:
    """Тесты для эндпоинта /api/city/search (city_search)."""
    
    url = reverse('city_search')

    @pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
    def test_prohibited_methods(self, api_client, method):
        """Проверяет, что запрещенные HTTP методы возвращают 405."""
        client_method = getattr(api_client, method)
        response = client_method(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_missing_query_parameter(self, api_client):
        """Проверяет валидацию обязательного параметра query."""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        # Сериализатор DRF возвращает ошибки в поле, соответствующем полю сериализатора
        assert 'query' in response_data

    def test_empty_query_parameter(self, api_client):
        """Проверяет обработку пустого параметра query."""
        response = api_client.get(f'{self.url}?query=')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        # Пустая строка может проходить валидацию сериализатора, но логика API возвращает ошибку
        assert 'detail' in response_data or 'query' in response_data

    @patch('city.api.City.objects.filter')
    def test_search_cities_success(self, mock_filter, api_client, mock_city):
        """Тест успешного поиска городов по подстроке с проверкой структуры ответа."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = [mock_city]
        mock_queryset.filter.return_value = mock_queryset
        mock_filter.return_value = mock_queryset
        
        response = api_client.get(f'{self.url}?query=Moscow')
        
        assert response.status_code == status.HTTP_200_OK
        mock_filter.assert_called_once_with(title__icontains='Moscow')
        mock_queryset.order_by.assert_called_once_with('title')
        
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 1
        assert response_data[0]['id'] == mock_city.id
        assert response_data[0]['title'] == mock_city.title

    @patch('city.api.City.objects.filter')
    def test_search_cities_with_country_filter(self, mock_filter, api_client, mock_city):
        """Тест поиска городов с дополнительной фильтрацией по стране."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = [mock_city]
        mock_filter.return_value = mock_queryset
        
        response = api_client.get(f'{self.url}?query=Moscow&country=RU')
        
        assert response.status_code == status.HTTP_200_OK
        mock_filter.assert_called_once_with(title__icontains='Moscow')
        mock_queryset.filter.assert_called_once_with(region__country__code='RU')

    @patch('city.api.City.objects.filter')
    def test_search_cities_empty_result(self, mock_filter, api_client):
        """Тест обработки пустого результата поиска."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = []
        mock_filter.return_value = mock_queryset
        
        response = api_client.get(f'{self.url}?query=NonexistentCity')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_invalid_serializer_data(self, api_client):
        """Тест обработки некорректных параметров сериализатора."""
        # Тест с некорректными параметрами сериализатора
        response = api_client.get(f'{self.url}?invalid_param=value')
        
        # Сериализатор должен пройти валидацию, так как query обязателен
        assert response.status_code == status.HTTP_400_BAD_REQUEST
