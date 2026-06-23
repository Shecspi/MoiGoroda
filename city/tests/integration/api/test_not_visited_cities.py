# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

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

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from dmr import Controller
from rest_framework import status
from rest_framework.test import APIClient

from city.api.common import GetNotVisitedCities
from city.models import City, VisitedCity
from country.models import Country
from region.models import Region, RegionType


@pytest.mark.integration
class TestGetNotVisitedCities:
    """Тесты для эндпоинта /api/city/not_visited (GetNotVisitedCities)."""

    url: str = reverse('api__get_not_visited_cities')

    def test_get_not_visited_cities_uses_django_modern_rest_controller(self) -> None:
        """Проверяет, что эндпоинт переведён с DRF generic view на django-modern-rest."""
        assert issubclass(GetNotVisitedCities, Controller)

    def test_guest_cannot_access(self, api_client: APIClient) -> None:
        """Проверяет, что неавторизованные пользователи не могут получить доступ к эндпоинту."""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
    def test_prohibited_methods(
        self, api_client: APIClient, authenticated_user: User, method: str
    ) -> None:
        """Проверяет, что запрещенные HTTP методы возвращают 405."""
        api_client.force_login(authenticated_user)
        client_method = getattr(api_client, method)
        response = client_method(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @patch('city.api.common.get_not_visited_cities')
    @patch('city.api.common.logger')
    def test_get_not_visited_cities_success(
        self,
        mock_logger: MagicMock,
        mock_get_not_visited_cities: MagicMock,
        api_client: APIClient,
        authenticated_user: User,
    ) -> None:
        """Тест успешного получения списка непосещенных городов."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__.return_value = []
        mock_get_not_visited_cities.return_value = mock_queryset
        api_client.force_login(authenticated_user)

        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
        mock_logger.info.assert_called_once()
        mock_get_not_visited_cities.assert_called_once_with(authenticated_user.pk, None)

    @patch('city.api.common.get_not_visited_cities')
    def test_get_not_visited_cities_with_country(
        self,
        mock_get_not_visited_cities: MagicMock,
        api_client: APIClient,
        authenticated_user: User,
    ) -> None:
        """Тест получения непосещенных городов с фильтрацией по стране."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__.return_value = []
        mock_get_not_visited_cities.return_value = mock_queryset
        api_client.force_login(authenticated_user)

        response = api_client.get(f'{self.url}?country=RU')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
        mock_get_not_visited_cities.assert_called_once_with(authenticated_user.pk, 'RU')

    @pytest.mark.django_db
    @patch('city.api.common.logger')
    def test_get_not_visited_cities_with_country_uses_constant_query_count(
        self,
        mock_logger: MagicMock,
        api_client: APIClient,
        authenticated_user: User,
    ) -> None:
        """Проверяет, что сериализация непосещённых городов не делает N+1 запросы."""
        country = Country.objects.create(name='Russia', fullname='Russia', code='RU')
        region_type = RegionType.objects.create(title='область')
        region = Region.objects.create(
            country=country,
            title='Test Region',
            type=region_type,
            full_name='Test Region',
            iso3166='RU-TEST',
        )
        cities = [
            City.objects.create(
                title=f'City {index}',
                country=country,
                region=region,
                coordinate_width=55.0 + index,
                coordinate_longitude=37.0 + index,
                image='',
            )
            for index in range(5)
        ]
        VisitedCity.objects.create(
            user=authenticated_user,
            city=cities[0],
            date_of_visit=date(2024, 1, 1),
            rating=5,
            is_first_visit=True,
        )
        api_client.force_login(authenticated_user)

        with CaptureQueriesContext(connection) as queries:
            response = api_client.get(f'{self.url}?country=RU')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 4
        assert len(queries) <= 4, [query['sql'][:200] for query in queries]
        mock_logger.info.assert_called_once()
