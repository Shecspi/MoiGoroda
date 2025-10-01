"""
Тесты для эндпоинта /api/city/visited/add (AddVisitedCity).

Покрывает:
- Добавление нового посещенного города
- Обработку дублирующихся записей (конфликт)
- Валидацию данных через сериализатор
- Проверку авторизации

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import date
from unittest.mock import MagicMock, patch
import pytest
from rest_framework import status
from django.urls import reverse

# Фикстуры импортируются автоматически из conftest.py


class TestAddVisitedCity:
    """Тесты для эндпоинта /api/city/visited/add (AddVisitedCity)."""
    
    url = reverse('api__add_visited_city')

    def test_guest_cannot_access(self, api_client):
        """Проверяет, что неавторизованные пользователи не могут получить доступ к эндпоинту."""
        response = api_client.post(self.url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('method', ['get', 'put', 'patch', 'delete'])
    def test_prohibited_methods(self, api_client, authenticated_user, method):
        """Проверяет, что запрещенные HTTP методы возвращают 405."""
        client_method = getattr(api_client, method)
        response = client_method(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @patch('city.api.VisitedCity.objects.filter')
    @patch('city.api.City.objects.get')
    @patch('city.api.get_number_of_visits_by_city')
    @patch('city.api.get_first_visit_date_by_city')
    @patch('city.api.get_last_visit_date_by_city')
    @patch('city.api.logger')
    def test_add_visited_city_success(
        self, mock_logger, mock_last_visit, mock_first_visit, mock_visits_count,
        mock_city_get, mock_visited_filter, api_client, authenticated_user, mock_city
    ):
        """Тест успешного добавления посещенного города с полным мокированием сериализатора."""
        mock_visited_filter.return_value.exists.return_value = False
        mock_city_get.return_value = mock_city
        mock_visits_count.return_value = 1
        mock_first_visit.return_value = '2024-01-15'
        mock_last_visit.return_value = '2024-01-15'
        
        data = {
            'city': mock_city.id,
            'date_of_visit': '2024-01-15',
            'rating': 5,
            'has_magnet': True,
            'impression': 'Great city!'
        }
        
        with patch('city.api.VisitedCity.objects.create') as mock_create, \
             patch('city.api.AddVisitedCitySerializer') as mock_serializer_class:
            
            # Мокаем сериализатор
            mock_serializer = MagicMock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.validated_data = {
                'city': mock_city,
                'date_of_visit': date(2024, 1, 15),
                'rating': 5,
                'has_magnet': True,
                'impression': 'Great city!'
            }
            mock_serializer.save.return_value = None
            # Используем простые строковые значения для избежания рекурсии
            mock_serializer.data = {
                'id': 1,
                'city': 1,
                'city_title': 'Moscow',
                'region_title': 'Moscow Region',
                'country': 'Russia',
                'date_of_visit': '2024-01-15',
                'rating': 5,
                'has_magnet': True,
                'impression': 'Great city!',
                'lat': 55.7558,
                'lon': 37.6173
            }
            mock_serializer_class.return_value = mock_serializer
            
            mock_created = MagicMock()
            mock_created.id = 1
            mock_created.city = mock_city
            mock_created.date_of_visit = date(2024, 1, 15)
            mock_created.rating = 5
            mock_created.has_magnet = True
            mock_created.impression = 'Great city!'
            mock_create.return_value = mock_created
            
            response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data['status'] == 'success'
        assert 'city' in response_data
        mock_logger.info.assert_called_once()

    @patch('city.api.VisitedCity.objects.filter')
    @patch('city.api.City.objects.get')
    @patch('city.api.logger')
    def test_add_duplicate_visited_city(
        self, mock_logger, mock_city_get, mock_visited_filter,
        api_client, authenticated_user, mock_city
    ):
        """Тест обработки дублирующегося посещения города."""
        mock_visited_filter.return_value.exists.return_value = True
        mock_city_get.return_value = mock_city
        
        data = {
            'city': mock_city.id,
            'date_of_visit': '2024-01-15',
            'rating': 5
        }
        
        with patch('city.api.AddVisitedCitySerializer') as mock_serializer_class:
            # Мокаем сериализатор
            mock_serializer = MagicMock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.validated_data = {
                'city': mock_city,
                'date_of_visit': date(2024, 1, 15),
                'rating': 5
            }
            mock_serializer_class.return_value = mock_serializer
            
            response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        response_data = response.json()
        assert response_data['status'] == 'success'
        assert 'уже сохранили посещение' in response_data['message']

    @patch('city.api.logger')
    def test_invalid_serializer_data(self, mock_logger, api_client, authenticated_user):
        """Тест обработки некорректных данных сериализатора."""
        data = {
            'city': 'invalid',
            'date_of_visit': 'invalid-date',
            'rating': 'invalid'
        }
        
        response = api_client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_logger.warning.assert_called_once()
