"""
Тесты для эндпоинта /api/city/list_by_country (city_list_by_country).

Покрывает:
- Получение списка городов по ID страны
- Валидацию обязательного параметра country_id
- Обработку пустых результатов

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


class TestCityListByCountry:
    """Тесты для эндпоинта /api/city/list_by_country (city_list_by_country)."""
    
    url = reverse('api__city_list_by_country')

    @pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
    def test_prohibited_methods(self, api_client, method):
        """Проверяет, что запрещенные HTTP методы возвращают 405."""
        client_method = getattr(api_client, method)
        response = client_method(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_missing_country_id_parameter(self, api_client):
        """Проверяет валидацию обязательного параметра country_id."""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert 'country_id является обязательным' in response_data['detail']

    @patch('city.api.City.objects.filter')
    def test_get_cities_by_country_success(self, mock_filter, api_client, mock_city):
        """Тест успешного получения городов по стране."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = [mock_city]
        mock_filter.return_value = mock_queryset
        
        response = api_client.get(f'{self.url}?country_id=1')
        
        assert response.status_code == status.HTTP_200_OK
        mock_filter.assert_called_once_with(country_id='1')
        mock_queryset.order_by.assert_called_once_with('title')

    @patch('city.api.City.objects.filter')
    def test_empty_cities_list_by_country(self, mock_filter, api_client):
        """Тест обработки пустого списка городов по стране."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = []
        mock_filter.return_value = mock_queryset
        
        response = api_client.get(f'{self.url}?country_id=999')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
