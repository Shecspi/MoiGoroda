"""
Интеграционные тесты для репозитория персональных коллекций.
"""

import uuid
from typing import Any

import pytest
from django.core.exceptions import ObjectDoesNotExist

from city.models import City, VisitedCity
from collection.models import PersonalCollection
from collection.repository import CollectionRepository
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType


@pytest.fixture
def setup_repository_data(django_user_model: Any) -> dict[str, Any]:
    """Создает тестовые данные для тестов репозитория."""
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
    VisitedCity.objects.create(
        user=user1, city=cities[1], date_of_visit='2023-02-01', is_first_visit=True, rating=4
    )

    # Создаем коллекции
    collection1 = PersonalCollection.objects.create(user=user1, title='Коллекция 1', is_public=True)
    collection1.city.set([cities[0], cities[1]])

    collection2 = PersonalCollection.objects.create(
        user=user1, title='Коллекция 2', is_public=False
    )
    collection2.city.set([cities[2]])

    collection3 = PersonalCollection.objects.create(user=user2, title='Коллекция 3', is_public=True)
    collection3.city.set(cities)

    return {
        'user1': user1,
        'user2': user2,
        'cities': cities,
        'collection1': collection1,
        'collection2': collection2,
        'collection3': collection3,
    }


@pytest.mark.django_db
@pytest.mark.integration
class TestGetPersonalCollectionsWithAnnotations:
    """Тесты для метода get_personal_collections_with_annotations."""

    def test_returns_user_collections_only(self, setup_repository_data: dict[str, Any]) -> None:
        """Проверяет что возвращаются только коллекции пользователя."""
        repository = CollectionRepository()
        user1 = setup_repository_data['user1']

        collections = repository.get_personal_collections_with_annotations(user1)

        assert collections.count() == 2
        for collection in collections:
            assert collection.user == user1

    def test_annotations_are_correct(self, setup_repository_data: dict[str, Any]) -> None:
        """Проверяет корректность аннотаций."""
        repository = CollectionRepository()
        user1 = setup_repository_data['user1']
        collection1 = setup_repository_data['collection1']

        collections = repository.get_personal_collections_with_annotations(user1)
        collection = collections.get(id=collection1.id)

        assert hasattr(collection, 'qty_of_cities')
        assert collection.qty_of_cities == 2
        assert hasattr(collection, 'qty_of_visited_cities')
        assert collection.qty_of_visited_cities == 2  # Оба города посещены

    def test_ordering_by_created_at_desc(self, setup_repository_data: dict[str, Any]) -> None:
        """Проверяет сортировку по дате создания (новые первыми)."""
        repository = CollectionRepository()
        user1 = setup_repository_data['user1']

        collections = list(repository.get_personal_collections_with_annotations(user1))

        # Проверяем что коллекции отсортированы по created_at (убывание)
        for i in range(len(collections) - 1):
            assert collections[i].created_at >= collections[i + 1].created_at


@pytest.mark.django_db
@pytest.mark.integration
class TestGetPersonalCollectionById:
    """Тесты для метода get_personal_collection_by_id."""

    def test_returns_collection_by_id(self, setup_repository_data: dict[str, Any]) -> None:
        """Проверяет получение коллекции по ID."""
        repository = CollectionRepository()
        collection1 = setup_repository_data['collection1']

        collection = repository.get_personal_collection_by_id(collection1.id)

        assert collection.id == collection1.id
        assert collection.title == collection1.title

    def test_raises_exception_for_nonexistent_id(
        self, setup_repository_data: dict[str, Any]
    ) -> None:
        """Проверяет что метод выбрасывает исключение для несуществующего ID."""
        repository = CollectionRepository()
        fake_id = uuid.uuid4()

        with pytest.raises(ObjectDoesNotExist):
            repository.get_personal_collection_by_id(fake_id)


@pytest.mark.django_db
@pytest.mark.integration
class TestGetPublicCollectionsWithAnnotations:
    """Тесты для метода get_public_collections_with_annotations."""

    def test_returns_only_public_collections(self, setup_repository_data: dict[str, Any]) -> None:
        """Проверяет что возвращаются только публичные коллекции."""
        repository = CollectionRepository()

        collections = repository.get_public_collections_with_annotations()

        assert collections.count() == 2  # collection1 и collection3
        for collection in collections:
            assert collection.is_public is True

    def test_annotations_include_qty_of_cities(self, setup_repository_data: dict[str, Any]) -> None:
        """Проверяет что аннотации включают количество городов."""
        repository = CollectionRepository()
        collection1 = setup_repository_data['collection1']

        collections = repository.get_public_collections_with_annotations()
        collection = collections.get(id=collection1.id)

        assert hasattr(collection, 'qty_of_cities')
        assert collection.qty_of_cities == 2

    def test_prefetch_first_15_cities(self, setup_repository_data: dict[str, Any]) -> None:
        """Проверяет что prefetch загружает первые 15 городов."""
        repository = CollectionRepository()
        collection3 = setup_repository_data['collection3']

        collections = repository.get_public_collections_with_annotations()
        collection = collections.get(id=collection3.id)

        assert hasattr(collection, 'first_15_cities')
        assert len(collection.first_15_cities) == 3
        # Проверяем что города отсортированы по алфавиту
        titles = [city.title for city in collection.first_15_cities]
        assert titles == sorted(titles)

    def test_ordering_by_created_at_desc(self, setup_repository_data: dict[str, Any]) -> None:
        """Проверяет сортировку по дате создания (новые первыми)."""
        repository = CollectionRepository()

        collections = list(repository.get_public_collections_with_annotations())

        # Проверяем что коллекции отсортированы по created_at (убывание)
        for i in range(len(collections) - 1):
            assert collections[i].created_at >= collections[i + 1].created_at
