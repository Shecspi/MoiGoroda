"""
Интеграционные тесты для API приложения country.
"""

from typing import Any

import pytest
from django.contrib.auth.models import User
from django.test import Client
from rest_framework import status

from city.models import City, VisitedCity
from country.models import Country, VisitedCountry, PartOfTheWorld, Location
from region.models import Region


@pytest.mark.django_db
@pytest.mark.integration
class TestGetPartsOfTheWorldAPI:
    """Тесты для API GetPartsOfTheWorld."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_returns_all_parts_of_the_world(
        self, client: Client, part_of_the_world: PartOfTheWorld
    ) -> None:
        """Проверяет что возвращаются все части света."""
        PartOfTheWorld.objects.create(name='Азия')

        response = client.get('/api/country/get_parts_of_the_world')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2


@pytest.mark.django_db
@pytest.mark.integration
class TestGetLocationsAPI:
    """Тесты для API GetLocations."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_returns_all_locations(self, client: Client, location: Location) -> None:
        """Проверяет что возвращаются все расположения."""
        response = client.get('/api/country/get_locations')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1


@pytest.mark.django_db
@pytest.mark.integration
class TestGetAllCountryAPI:
    """Тесты для API GetAllCountry."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def countries(self) -> list[Country]:
        """Создает тестовые страны."""
        return [
            Country.objects.create(name='Россия', code='RU'),
            Country.objects.create(name='Германия', code='DE'),
            Country.objects.create(name='Франция', code='FR'),
        ]

    def test_returns_all_countries(self, client: Client, countries: list[Country]) -> None:
        """Проверяет что возвращаются все страны."""
        response = client.get('/api/country/all')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3


@pytest.mark.django_db
@pytest.mark.integration
class TestGetVisitedCountryAPI:
    """Тесты для API GetVisitedCountry."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_requires_authentication(self, client: Client) -> None:
        """Проверяет что требуется авторизация."""
        response = client.get('/api/country/visited')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_user_visited_countries(self, client: Client, user: User) -> None:
        """Проверяет что возвращаются только страны пользователя."""
        russia = Country.objects.create(name='Россия', code='RU')
        germany = Country.objects.create(name='Германия', code='DE')

        VisitedCountry.objects.create(country=russia, user=user)

        # Другой пользователь посещает Германию
        other_user = User.objects.create_user(username='other', password='pass')
        VisitedCountry.objects.create(country=germany, user=other_user)

        client.force_login(user)
        response = client.get('/api/country/visited')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['code'] == 'RU'


@pytest.mark.django_db
@pytest.mark.integration
class TestAddVisitedCountryAPI:
    """Тесты для API AddVisitedCountry."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_requires_authentication(self, client: Client) -> None:
        """Проверяет что требуется авторизация."""
        response = client.post('/api/country/add', {'code': 'RU'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_adds_visited_country(self, client: Client, user: User) -> None:
        """Проверяет добавление посещенной страны."""
        Country.objects.create(name='Россия', code='RU')

        client.force_login(user)
        response = client.post('/api/country/add', {'code': 'RU'})

        assert response.status_code == status.HTTP_200_OK
        assert VisitedCountry.objects.filter(user=user, country__code='RU').exists()

    def test_returns_error_for_non_existent_country(self, client: Client, user: User) -> None:
        """Проверяет ошибку при попытке добавить несуществующую страну."""
        client.force_login(user)
        response = client.post('/api/country/add', {'code': 'XX'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_error_for_already_visited_country(self, client: Client, user: User) -> None:
        """Проверяет ошибку при попытке добавить уже посещенную страну."""
        country = Country.objects.create(name='Россия', code='RU')
        VisitedCountry.objects.create(country=country, user=user)

        client.force_login(user)
        response = client.post('/api/country/add', {'code': 'RU'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.integration
class TestDeleteVisitedCountryAPI:
    """Тесты для API DeleteVisitedCountry."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_requires_authentication(self, client: Client) -> None:
        """Проверяет что требуется авторизация."""
        response = client.delete('/api/country/delete/RU')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_deletes_visited_country(self, client: Client, user: User) -> None:
        """Проверяет удаление посещенной страны."""
        country = Country.objects.create(name='Россия', code='RU')
        VisitedCountry.objects.create(country=country, user=user)

        client.force_login(user)
        response = client.delete('/api/country/delete/RU')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not VisitedCountry.objects.filter(user=user, country=country).exists()

    def test_returns_404_for_non_existent_country(self, client: Client, user: User) -> None:
        """Проверяет ошибку 404 для несуществующей страны."""
        client.force_login(user)
        response = client.delete('/api/country/delete/XX')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_deletes_only_user_country(self, client: Client, user: User) -> None:
        """Проверяет что удаляется только страна текущего пользователя."""
        country = Country.objects.create(name='Россия', code='RU')
        other_user = User.objects.create_user(username='other', password='pass')

        VisitedCountry.objects.create(country=country, user=user)
        VisitedCountry.objects.create(country=country, user=other_user)

        client.force_login(user)
        response = client.delete('/api/country/delete/RU')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Пользовательская запись удалена
        assert not VisitedCountry.objects.filter(user=user, country=country).exists()
        # Запись другого пользователя осталась
        assert VisitedCountry.objects.filter(user=other_user, country=country).exists()


@pytest.mark.django_db
@pytest.mark.integration
class TestCountryListWithVisitedCitiesAPI:
    """Тесты для API country_list_with_visited_cities."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def setup_data(self, user: User, region_type: Any) -> dict[str, Any]:
        """Создает данные для тестов."""
        russia = Country.objects.create(name='Россия', code='RU')
        germany = Country.objects.create(name='Германия', code='DE')
        france = Country.objects.create(name='Франция', code='FR')  # Без городов

        region_ru = Region.objects.create(
            title='Москва',
            country=russia,
            type=region_type,
            iso3166='RU-API',
            full_name='г. Москва',
        )
        region_de = Region.objects.create(
            title='Берлин', country=germany, type=region_type, iso3166='DE-API', full_name='Берлин'
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

        VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=True)

        return {
            'user': user,
            'russia': russia,
            'germany': germany,
            'france': france,
            'moscow': moscow,
            'berlin': berlin,
        }

    def test_anonymous_user_gets_all_countries_with_cities(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет что анонимный пользователь получает все страны с городами."""
        response = client.get('/api/country/list_by_cities')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Россия и Германия (у Франции нет городов)
        assert len(data) == 2

    def test_authenticated_user_gets_countries_sorted_by_visited(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет что авторизованный пользователь получает отсортированный список."""
        user = setup_data['user']
        client.force_login(user)

        response = client.get('/api/country/list_by_cities')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Первой должна быть Россия (есть посещенные города)
        assert data[0]['code'] == 'RU'
