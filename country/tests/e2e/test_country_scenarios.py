"""
E2E тесты для полных сценариев работы со странами.
"""

from typing import Any

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from rest_framework import status

from city.models import City, VisitedCity
from country.models import Country, VisitedCountry
from region.models import Region


@pytest.mark.django_db
@pytest.mark.e2e
class TestCountryFullWorkflow:
    """Сквозные тесты для полного сценария работы со странами."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def setup_countries(self, user: User, region_type: Any) -> dict[str, Any]:
        """Создает полноценную структуру стран и городов."""
        russia = Country.objects.create(name='Россия', code='RU')
        germany = Country.objects.create(name='Германия', code='DE')
        france = Country.objects.create(name='Франция', code='FR')

        region_ru = Region.objects.create(
            title='Москва',
            country=russia,
            type=region_type,
            iso3166='RU-E2E',
            full_name='г. Москва',
        )
        region_de = Region.objects.create(
            title='Берлин', country=germany, type=region_type, iso3166='DE-E2E', full_name='Берлин'
        )
        region_fr = Region.objects.create(
            title='Париж', country=france, type=region_type, iso3166='FR-E2E', full_name='Париж'
        )

        moscow = City.objects.create(
            title='Москва',
            region=region_ru,
            country=russia,
            coordinate_width='55.7558',
            coordinate_longitude='37.6173',
        )
        berlin = City.objects.create(
            title='Берлин',
            region=region_de,
            country=germany,
            coordinate_width='52.5200',
            coordinate_longitude='13.4050',
        )
        paris = City.objects.create(
            title='Париж',
            region=region_fr,
            country=france,
            coordinate_width='48.8566',
            coordinate_longitude='2.3522',
        )

        return {
            'user': user,
            'russia': russia,
            'germany': germany,
            'france': france,
            'moscow': moscow,
            'berlin': berlin,
            'paris': paris,
        }

    def test_user_can_view_country_map(
        self, client: Client, setup_countries: dict[str, Any]
    ) -> None:
        """Пользователь может просматривать карту стран."""
        response = client.get(reverse('country_map'))

        assert response.status_code == 200
        assert 'page_title' in response.context

    def test_user_journey_adding_visited_countries_via_api(
        self, client: Client, setup_countries: dict[str, Any]
    ) -> None:
        """Сценарий: пользователь добавляет посещенные страны через API."""
        user = setup_countries['user']
        client.force_login(user)

        # 1. Проверяем что у пользователя нет посещенных стран
        response = client.get('/api/country/visited')
        assert len(response.json()) == 0

        # 2. Добавляем Россию
        response = client.post('/api/country/add', {'code': 'RU'})
        assert response.status_code == status.HTTP_200_OK

        # 3. Проверяем что Россия добавилась
        response = client.get('/api/country/visited')
        data = response.json()
        assert len(data) == 1
        assert data[0]['code'] == 'RU'

        # 4. Добавляем Германию
        response = client.post('/api/country/add', {'code': 'DE'})
        assert response.status_code == status.HTTP_200_OK

        # 5. Проверяем что обе страны в списке
        response = client.get('/api/country/visited')
        data = response.json()
        assert len(data) == 2

        # 6. Пытаемся добавить Россию повторно - должна быть ошибка
        response = client.post('/api/country/add', {'code': 'RU'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_journey_deleting_visited_country(
        self, client: Client, setup_countries: dict[str, Any]
    ) -> None:
        """Сценарий: пользователь удаляет посещенную страну."""
        user = setup_countries['user']
        russia = setup_countries['russia']
        client.force_login(user)

        # Добавляем страну
        VisitedCountry.objects.create(country=russia, user=user)

        # Проверяем что она есть
        response = client.get('/api/country/visited')
        assert len(response.json()) == 1

        # Удаляем страну
        response = client.delete('/api/country/delete/RU')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем что список пуст
        response = client.get('/api/country/visited')
        assert len(response.json()) == 0

    def test_visiting_cities_adds_countries_to_list(
        self, client: Client, setup_countries: dict[str, Any]
    ) -> None:
        """Сценарий: посещение городов отражается в списке стран с посещенными городами."""
        user = setup_countries['user']
        moscow = setup_countries['moscow']
        berlin = setup_countries['berlin']

        client.force_login(user)

        # Посещаем Москву
        VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=True)

        # Проверяем список стран с посещенными городами
        response = client.get('/api/country/list_by_cities')
        data = response.json()

        # Должна быть Россия с 1 посещенным городом
        russia_data = next((c for c in data if c['code'] == 'RU'), None)
        assert russia_data is not None
        assert russia_data['number_of_visited_cities'] == 1

        # Посещаем Берлин
        VisitedCity.objects.create(user=user, city=berlin, rating=4, is_first_visit=True)

        response = client.get('/api/country/list_by_cities')
        data = response.json()

        # Теперь должно быть 2 страны
        assert len(data) >= 2

    def test_anonymous_user_sees_all_countries_with_cities(
        self, client: Client, setup_countries: dict[str, Any]
    ) -> None:
        """Анонимный пользователь видит все страны, у которых есть города."""
        response = client.get('/api/country/list_by_cities')

        assert response.status_code == 200
        data = response.json()
        # Все 3 страны имеют города
        assert len(data) == 3

    def test_case_insensitive_country_code_in_delete(
        self, client: Client, setup_countries: dict[str, Any]
    ) -> None:
        """Проверяет что код страны при удалении регистронезависим."""
        user = setup_countries['user']
        russia = setup_countries['russia']
        client.force_login(user)

        VisitedCountry.objects.create(country=russia, user=user)

        # Удаляем используя нижний регистр
        response = client.delete('/api/country/delete/ru')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not VisitedCountry.objects.filter(user=user, country=russia).exists()
