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

# Any больше не используется, так как заменили на точные типы
from unittest.mock import MagicMock, patch
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse  # type: ignore


class TestCitySearch:
    """Тесты для эндпоинта /api/city/search (city_search)."""

    url: str = reverse('city_search')

    @pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
    def test_prohibited_methods(self, api_client: APIClient, method: str) -> None:
        """Проверяет, что запрещенные HTTP методы возвращают 405."""
        client_method = getattr(api_client, method)
        response = client_method(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_missing_query_parameter(self, api_client: APIClient) -> None:
        """Проверяет валидацию обязательного параметра query."""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        # Сериализатор DRF возвращает ошибки в поле, соответствующем полю сериализатора
        assert 'query' in response_data

    def test_empty_query_parameter(self, api_client: APIClient) -> None:
        """Проверяет обработку пустого параметра query."""
        response = api_client.get(f'{self.url}?query=')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        # Пустая строка может проходить валидацию сериализатора, но логика API возвращает ошибку
        assert 'detail' in response_data or 'query' in response_data

    @patch('city.services.search.CitySearchService.search_cities')
    def test_search_cities_success(
        self, mock_search: MagicMock, api_client: APIClient, mock_city: MagicMock
    ) -> None:
        """Тест успешного поиска городов по подстроке с проверкой структуры ответа."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = MagicMock(return_value=iter([mock_city]))
        mock_search.return_value = mock_queryset

        response = api_client.get(f'{self.url}?query=Moscow')

        assert response.status_code == status.HTTP_200_OK
        mock_search.assert_called_once_with(query='Moscow', country=None)

        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 1  # type: ignore
        assert response_data[0]['id'] == mock_city.id
        assert response_data[0]['title'] == mock_city.title

    @patch('city.services.search.CitySearchService.search_cities')
    def test_search_cities_with_country_filter(
        self, mock_search: MagicMock, api_client: APIClient, mock_city: MagicMock
    ) -> None:
        """Тест поиска городов с дополнительной фильтрацией по стране."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = MagicMock(return_value=iter([mock_city]))
        mock_search.return_value = mock_queryset

        response = api_client.get(f'{self.url}?query=Moscow&country=RU')

        assert response.status_code == status.HTTP_200_OK
        mock_search.assert_called_once_with(query='Moscow', country='RU')

    @patch('city.services.search.CitySearchService.search_cities')
    def test_search_cities_empty_result(
        self, mock_search: MagicMock, api_client: APIClient
    ) -> None:
        """Тест обработки пустого результата поиска."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = MagicMock(return_value=iter([]))
        mock_search.return_value = mock_queryset

        response = api_client.get(f'{self.url}?query=NonexistentCity')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_invalid_serializer_data(self, api_client: APIClient) -> None:
        """Тест обработки некорректных параметров сериализатора."""
        # Тест с некорректными параметрами сериализатора
        response = api_client.get(f'{self.url}?invalid_param=value')

        # Сериализатор должен пройти валидацию, так как query обязателен
        assert response.status_code == status.HTTP_400_BAD_REQUEST
