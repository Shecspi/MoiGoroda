"""
Интеграционные тесты для сервиса персональных коллекций.
"""

import uuid
from typing import Any

import pytest
from django.http import Http404

from city.models import City, VisitedCity
from collection.models import PersonalCollection
from collection.services import PersonalCollectionService
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType


@pytest.fixture
def setup_service_data(django_user_model: Any) -> dict[str, Any]:
    """Создает тестовые данные для тестов сервиса."""
    # Создаем пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='testpass123')
    user2 = django_user_model.objects.create_user(username='user2', password='testpass123')

    # Создаем страну, регион и города
    part_of_world = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name='Восточная Европа', part_of_the_world=part_of_world)
    country = Country.objects.create(
        name='Россия', code='RU', fullname='Российская Федерация', location=location
    )
    region_type = RegionType.objects.create(title='Область')
    area = Area.objects.create(country=country, title='Центральный')
    region = Region.objects.create(
        title='Московская',
        country=country,
        type=region_type,
        area=area,
        iso3166='RU-MOS',
        full_name='Московская область',
    )

    cities = [
        City.objects.create(
            title='Москва',
            country=country,
            region=region,
            coordinate_width=55.75,
            coordinate_longitude=37.62,
        ),
        City.objects.create(
            title='Санкт-Петербург',
            country=country,
            region=region,
            coordinate_width=59.93,
            coordinate_longitude=30.34,
        ),
        City.objects.create(
            title='Казань',
            country=country,
            region=region,
            coordinate_width=55.79,
            coordinate_longitude=49.12,
        ),
    ]

    # Создаем посещенные города для user1
    VisitedCity.objects.create(
        user=user1, city=cities[0], date_of_visit='2023-01-01', is_first_visit=True, rating=5
    )

    # Создаем коллекции
    public_collection = PersonalCollection.objects.create(
        user=user1, title='Публичная коллекция', is_public=True
    )
    public_collection.city.set([cities[0], cities[1]])

    private_collection = PersonalCollection.objects.create(
        user=user1, title='Приватная коллекция', is_public=False
    )
    private_collection.city.set([cities[0]])

    return {
        'user1': user1,
        'user2': user2,
        'cities': cities,
        'public_collection': public_collection,
        'private_collection': private_collection,
    }


@pytest.mark.django_db
@pytest.mark.integration
class TestGetCollectionWithAccessCheck:
    """Тесты для метода get_collection_with_access_check."""

    def test_owner_can_access_private_collection(self, setup_service_data: dict[str, Any]) -> None:
        """Проверяет что владелец может получить доступ к приватной коллекции."""
        service = PersonalCollectionService()
        user1 = setup_service_data['user1']
        collection = setup_service_data['private_collection']

        result = service.get_collection_with_access_check(collection.id, user1)

        assert result.id == collection.id

    def test_owner_can_access_public_collection(self, setup_service_data: dict[str, Any]) -> None:
        """Проверяет что владелец может получить доступ к публичной коллекции."""
        service = PersonalCollectionService()
        user1 = setup_service_data['user1']
        collection = setup_service_data['public_collection']

        result = service.get_collection_with_access_check(collection.id, user1)

        assert result.id == collection.id

    def test_anonymous_can_access_public_collection(
        self, setup_service_data: dict[str, Any]
    ) -> None:
        """Проверяет что неавторизованный пользователь может получить доступ к публичной коллекции."""
        service = PersonalCollectionService()
        collection = setup_service_data['public_collection']
        anonymous_user = type('User', (), {'is_authenticated': False})()

        result = service.get_collection_with_access_check(collection.id, anonymous_user)

        assert result.id == collection.id

    def test_anonymous_cannot_access_private_collection(
        self, setup_service_data: dict[str, Any]
    ) -> None:
        """Проверяет что неавторизованный пользователь не может получить доступ к приватной коллекции."""
        service = PersonalCollectionService()
        collection = setup_service_data['private_collection']
        anonymous_user = type('User', (), {'is_authenticated': False})()

        with pytest.raises(Http404):
            service.get_collection_with_access_check(collection.id, anonymous_user)

    def test_other_user_cannot_access_private_collection(
        self, setup_service_data: dict[str, Any]
    ) -> None:
        """Проверяет что другой пользователь не может получить доступ к приватной коллекции."""
        service = PersonalCollectionService()
        user2 = setup_service_data['user2']
        collection = setup_service_data['private_collection']

        with pytest.raises(Http404):
            service.get_collection_with_access_check(collection.id, user2)

    def test_other_user_can_access_public_collection(
        self, setup_service_data: dict[str, Any]
    ) -> None:
        """Проверяет что другой пользователь может получить доступ к публичной коллекции."""
        service = PersonalCollectionService()
        user2 = setup_service_data['user2']
        collection = setup_service_data['public_collection']

        result = service.get_collection_with_access_check(collection.id, user2)

        assert result.id == collection.id

    def test_nonexistent_collection_raises_404(self, setup_service_data: dict[str, Any]) -> None:
        """Проверяет что несуществующая коллекция вызывает 404."""
        service = PersonalCollectionService()
        user1 = setup_service_data['user1']
        fake_id = uuid.uuid4()

        with pytest.raises(Http404):
            service.get_collection_with_access_check(fake_id, user1)


@pytest.mark.django_db
@pytest.mark.integration
class TestGetCitiesForCollection:
    """Тесты для метода get_cities_for_collection."""

    def test_returns_all_cities_without_filter(self, setup_service_data: dict[str, Any]) -> None:
        """Проверяет возврат всех городов без фильтра."""
        service = PersonalCollectionService()
        user1 = setup_service_data['user1']
        collection = setup_service_data['public_collection']

        cities, statistics = service.get_cities_for_collection(
            collection.id, user1, filter_value=None
        )

        assert cities.count() == 2
        assert statistics['filter'] == ''

    def test_returns_visited_cities_with_filter(self, setup_service_data: dict[str, Any]) -> None:
        """Проверяет возврат только посещенных городов с фильтром."""
        service = PersonalCollectionService()
        user1 = setup_service_data['user1']
        collection = setup_service_data['public_collection']

        cities, statistics = service.get_cities_for_collection(
            collection.id, user1, filter_value='visited'
        )

        assert cities.count() == 1
        assert statistics['filter'] == 'visited'

    def test_returns_not_visited_cities_with_filter(
        self, setup_service_data: dict[str, Any]
    ) -> None:
        """Проверяет возврат только непосещенных городов с фильтром."""
        service = PersonalCollectionService()
        user1 = setup_service_data['user1']
        collection = setup_service_data['public_collection']

        cities, statistics = service.get_cities_for_collection(
            collection.id, user1, filter_value='not_visited'
        )

        assert cities.count() == 1
        assert statistics['filter'] == 'not_visited'
