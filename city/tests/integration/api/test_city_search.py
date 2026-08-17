# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

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
from django.urls import reverse
from dmr import Controller
from rest_framework import status
from rest_framework.test import APIClient

from city.api.lookups import CitySearchController
from city.models import City
from country.models import Country
from region.models import Region, RegionType


@pytest.mark.integration
class TestCitySearch:
    """Тесты для эндпоинта /api/city/search (city_search)."""

    url: str = reverse('city_search')

    def test_uses_django_modern_rest_controller(self) -> None:
        assert issubclass(CitySearchController, Controller)

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
        assert 'detail' in response_data
        assert 'query' in str(response_data['detail'])

    def test_empty_query_parameter(self, api_client: APIClient) -> None:
        """Проверяет обработку пустого параметра query."""
        response = api_client.get(f'{self.url}?query=')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert 'detail' in response_data

    @patch('city.services.search.CitySearchService.search_cities')
    def test_rejects_whitespace_only_query(
        self,
        mock_search: MagicMock,
        api_client: APIClient,
    ) -> None:
        response = api_client.get(self.url, {'query': '   '})

        assert response.status_code == 400
        assert 'query' in str(response.json())
        mock_search.assert_not_called()

    def test_rejects_query_longer_than_100_characters(
        self,
        api_client: APIClient,
    ) -> None:
        response = api_client.get(self.url, {'query': 'М' * 101})

        assert response.status_code == 400
        assert 'query' in str(response.json())

    @patch('city.services.search.CitySearchService.search_cities')
    def test_search_cities_success(
        self, mock_search: MagicMock, api_client: APIClient, mock_city: MagicMock
    ) -> None:
        """Тест успешного поиска городов по подстроке с проверкой структуры ответа."""
        # Настройка мока города с регионом и страной
        mock_city.id = 1
        mock_city.title = 'Moscow'
        mock_city.region = MagicMock()
        mock_city.region.full_name = 'Московская область'
        mock_city.country = MagicMock()
        mock_city.country.name = 'Russia'

        mock_queryset = MagicMock()
        mock_queryset.__iter__ = MagicMock(return_value=iter([mock_city]))
        mock_search.return_value = mock_queryset

        response = api_client.get(f'{self.url}?query=Moscow')

        assert response.status_code == status.HTTP_200_OK
        mock_search.assert_called_once_with(
            query='Moscow', country=None, region=None, limit=50
        )

        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 1
        assert response_data[0]['id'] == mock_city.id
        assert response_data[0]['title'] == mock_city.title
        assert response_data[0]['region'] == mock_city.region.full_name
        assert response_data[0]['country'] == mock_city.country.name

    @patch('city.services.search.CitySearchService.search_cities')
    def test_search_cities_with_country_filter(
        self, mock_search: MagicMock, api_client: APIClient, mock_city: MagicMock
    ) -> None:
        """Тест поиска городов с дополнительной фильтрацией по стране."""
        # Настройка мока города с регионом и страной
        mock_city.id = 1
        mock_city.title = 'Moscow'
        mock_city.region = MagicMock()
        mock_city.region.full_name = 'Московская область'
        mock_city.country = MagicMock()
        mock_city.country.name = 'Russia'

        mock_queryset = MagicMock()
        mock_queryset.__iter__ = MagicMock(return_value=iter([mock_city]))
        mock_search.return_value = mock_queryset

        response = api_client.get(f'{self.url}?query=Moscow&country=RU')

        assert response.status_code == status.HTTP_200_OK
        mock_search.assert_called_once_with(
            query='Moscow', country='RU', region=None, limit=50
        )

        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 1
        assert response_data[0]['id'] == mock_city.id
        assert response_data[0]['title'] == mock_city.title
        assert response_data[0]['region'] == mock_city.region.full_name
        assert (
            response_data[0]['country'] is None
        )  # Страна должна быть скрыта, так как country указан в URL

    @patch('city.services.search.CitySearchService.search_cities')
    def test_search_cities_with_region_code(
        self,
        mock_search: MagicMock,
        api_client: APIClient,
        mock_city: MagicMock,
    ) -> None:
        mock_city.id = 1
        mock_city.title = 'Москва'
        mock_city.region.full_name = 'Москва'
        mock_city.country.name = 'Россия'
        mock_search.return_value = [mock_city]

        response = api_client.get(self.url, {'query': 'Моск', 'region': 'RU-MOW'})

        assert response.status_code == status.HTTP_200_OK
        mock_search.assert_called_once_with(
            query='Моск',
            country=None,
            region='RU-MOW',
            limit=50,
        )
        assert response.json()[0]['country'] == 'Россия'

    @pytest.mark.parametrize('removed_param', ['country_id', 'region_id'])
    def test_rejects_removed_numeric_filters(
        self,
        api_client: APIClient,
        removed_param: str,
    ) -> None:
        response = api_client.get(self.url, {'query': 'Моск', removed_param: '1'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize('invalid_country', ['', '  ', 'R', 'R ', 'RUS'])
    def test_rejects_country_code_that_is_not_two_characters(
        self,
        api_client: APIClient,
        invalid_country: str,
    ) -> None:
        response = api_client.get(
            self.url,
            {'query': 'Моск', 'country': invalid_country},
        )

        assert response.status_code == 400
        assert 'country' in str(response.json())

    @pytest.mark.parametrize('invalid_region', ['', '   ', 'R' * 11])
    def test_rejects_blank_or_overlong_region_code(
        self,
        api_client: APIClient,
        invalid_region: str,
    ) -> None:
        response = api_client.get(
            self.url,
            {'query': 'Моск', 'region': invalid_region},
        )

        assert response.status_code == 400
        assert 'region' in str(response.json())

    @pytest.mark.parametrize('invalid_limit', ['0', 'not-a-number'])
    def test_rejects_zero_or_non_integer_limit(
        self,
        api_client: APIClient,
        invalid_limit: str,
    ) -> None:
        response = api_client.get(
            self.url,
            {'query': 'Моск', 'limit': invalid_limit},
        )

        assert response.status_code == 400
        assert 'limit' in str(response.json())

    def test_rejects_limit_above_200(self, api_client: APIClient) -> None:
        response = api_client.get(self.url, {'query': 'Моск', 'limit': '201'})

        assert response.status_code == 400
        assert 'limit' in str(response.json())

    @pytest.mark.parametrize(
        'location_filter',
        [{'country': 'ZZ'}, {'region': 'ZZ-UNKNOWN'}],
    )
    @pytest.mark.django_db
    def test_unknown_valid_location_code_returns_empty_list(
        self,
        api_client: APIClient,
        location_filter: dict[str, str],
    ) -> None:
        country = Country.objects.create(name='Тестовая страна', code='RU')
        region_type = RegionType.objects.create(title='Тестовый тип')
        region = Region.objects.create(
            country=country,
            title='Тестовый регион',
            type=region_type,
            full_name='Тестовый регион',
            iso3166='RU-MOW',
        )
        City.objects.create(
            title='Совпадающий город',
            country=country,
            region=region,
            coordinate_width=55.75,
            coordinate_longitude=37.62,
        )

        unfiltered_response = api_client.get(
            self.url,
            {'query': 'Совпадающий'},
        )
        response = api_client.get(
            self.url,
            {'query': 'Совпадающий', **location_filter},
        )

        assert unfiltered_response.status_code == 200
        assert [item['title'] for item in unfiltered_response.json()] == [
            'Совпадающий город'
        ]
        assert response.status_code == 200
        assert response.json() == []

    @patch('city.services.search.CitySearchService.search_cities')
    def test_search_cities_with_custom_limit(
        self, mock_search: MagicMock, api_client: APIClient, mock_city: MagicMock
    ) -> None:
        """Тест поиска городов с пользовательским лимитом."""
        # Настройка мока города с регионом и страной
        mock_city.id = 1
        mock_city.title = 'Moscow'
        mock_city.region = MagicMock()
        mock_city.region.full_name = 'Московская область'
        mock_city.country = MagicMock()
        mock_city.country.name = 'Russia'

        mock_queryset = MagicMock()
        mock_queryset.__iter__ = MagicMock(return_value=iter([mock_city]))
        mock_search.return_value = mock_queryset

        response = api_client.get(f'{self.url}?query=Moscow&limit=20')

        assert response.status_code == status.HTTP_200_OK
        mock_search.assert_called_once_with(
            query='Moscow', country=None, region=None, limit=20
        )

        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 1
        assert response_data[0]['id'] == mock_city.id
        assert response_data[0]['title'] == mock_city.title
        assert response_data[0]['region'] == mock_city.region.full_name
        assert response_data[0]['country'] == mock_city.country.name

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

    @patch('city.services.search.CitySearchService.search_cities')
    def test_search_cities_without_region(
        self, mock_search: MagicMock, api_client: APIClient, mock_city: MagicMock
    ) -> None:
        """Тест поиска городов без указанного региона."""
        # Настройка мока города без региона
        mock_city.id = 1
        mock_city.title = 'Berlin'
        mock_city.region = None
        mock_city.country = MagicMock()
        mock_city.country.name = 'Germany'

        mock_queryset = MagicMock()
        mock_queryset.__iter__ = MagicMock(return_value=iter([mock_city]))
        mock_search.return_value = mock_queryset

        response = api_client.get(f'{self.url}?query=Berlin')

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 1
        assert response_data[0]['id'] == mock_city.id
        assert response_data[0]['title'] == mock_city.title
        assert response_data[0]['region'] is None
        assert response_data[0]['country'] == mock_city.country.name

    @patch('city.services.search.CitySearchService.search_cities')
    def test_search_cities_hide_country_when_country_in_url(
        self, mock_search: MagicMock, api_client: APIClient, mock_city: MagicMock
    ) -> None:
        """Тест поиска городов с скрытием страны, когда country указан в URL."""
        # Настройка мока города
        mock_city.id = 1
        mock_city.title = 'Paris'
        mock_city.region = MagicMock()
        mock_city.region.full_name = 'Регион Иль-де-Франс'
        mock_city.country = MagicMock()
        mock_city.country.name = 'France'

        mock_queryset = MagicMock()
        mock_queryset.__iter__ = MagicMock(return_value=iter([mock_city]))
        mock_search.return_value = mock_queryset

        # Тест с country в URL - страна должна быть скрыта
        response = api_client.get(f'{self.url}?query=Paris&country=FR')

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 1
        assert response_data[0]['id'] == mock_city.id
        assert response_data[0]['title'] == mock_city.title
        assert response_data[0]['region'] == mock_city.region.full_name
        assert response_data[0]['country'] is None  # Страна должна быть скрыта
