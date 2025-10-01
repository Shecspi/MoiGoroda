"""
Тесты для эндпоинта /api/city/list_by_region (city_list_by_region).

Покрывает:
- Получение списка городов по ID региона
- Валидацию обязательного параметра region_id
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


class TestCityListByRegion:
    """Тесты для эндпоинта /api/city/list_by_region (city_list_by_region)."""
    
    url = reverse('api__city_list_by_region')

    @pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
    def test_prohibited_methods(self, api_client, method):
        """Проверяет, что запрещенные HTTP методы возвращают 405."""
        client_method = getattr(api_client, method)
        response = client_method(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_missing_region_id_parameter(self, api_client):
        """Проверяет валидацию обязательного параметра region_id."""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert 'region_id является обязательным' in response_data['detail']

    @patch('city.api.City.objects.filter')
    def test_get_cities_by_region_success(self, mock_filter, api_client, mock_city):
        """Тест успешного получения городов по региону."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = [mock_city]
        mock_filter.return_value = mock_queryset
        
        response = api_client.get(f'{self.url}?region_id=1')
        
        assert response.status_code == status.HTTP_200_OK
        mock_filter.assert_called_once_with(region_id='1')
        mock_queryset.order_by.assert_called_once_with('title')

    @patch('city.api.City.objects.filter')
    def test_empty_cities_list_by_region(self, mock_filter, api_client):
        """Тест обработки пустого списка городов по региону."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = []
        mock_filter.return_value = mock_queryset
        
        response = api_client.get(f'{self.url}?region_id=999')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
