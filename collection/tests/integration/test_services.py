"""
Интеграционные тесты для сервисов приложения collection.
"""

from typing import Any

import pytest
from django.contrib.auth.models import User

from city.models import City, VisitedCity
from collection.models import Collection
from collection.services import get_all_cities_from_collection
from country.models import Country
from region.models import Region


@pytest.mark.django_db
@pytest.mark.integration
class TestGetAllCitiesFromCollection:
    """Тесты для функции get_all_cities_from_collection."""

    @pytest.fixture
    def setup_data(self, region_type: Any) -> dict[str, Any]:
        """Создает данные для тестов."""
        country = Country.objects.create(name='Россия', code='RU')
        region = Region.objects.create(
            title='Москва', country=country, type=region_type, iso3166='RU-MOW', full_name='Москва'
        )

        city1 = City.objects.create(
            title='Москва',
            region=region,
            country=country,
            coordinate_width='55.7558',
            coordinate_longitude='37.6173',
        )
        city2 = City.objects.create(
            title='Санкт-Петербург',
            region=region,
            country=country,
            coordinate_width='59.9343',
            coordinate_longitude='30.3351',
        )
        city3 = City.objects.create(
            title='Казань',
            region=region,
            country=country,
            coordinate_width='55.8304',
            coordinate_longitude='49.0661',
        )

        collection = Collection.objects.create(title='Столицы')
        collection.city.set([city1, city2])

        user = User.objects.create_user(username='testuser', password='testpass')

        return {
            'user': user,
            'collection': collection,
            'city1': city1,
            'city2': city2,
            'city3': city3,
        }

    def test_returns_all_cities_from_collection_without_user(
        self, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет что функция возвращает все города коллекции для неавторизованного."""
        collection = setup_data['collection']

        cities = get_all_cities_from_collection(collection.id)

        assert cities.count() == 2
        assert hasattr(cities.first(), 'is_visited')
        assert cities.first().is_visited is False  # type: ignore[union-attr]

    def test_returns_all_cities_from_collection_with_user(self, setup_data: dict[str, Any]) -> None:
        """Проверяет что функция возвращает все города коллекции для авторизованного."""
        user = setup_data['user']
        collection = setup_data['collection']
        city1 = setup_data['city1']

        # Добавляем посещение
        VisitedCity.objects.create(user=user, city=city1, rating=3, is_first_visit=True)

        cities = get_all_cities_from_collection(collection.id, user)

        assert cities.count() == 2

    def test_annotations_for_authenticated_user(self, setup_data: dict[str, Any]) -> None:
        """Проверяет наличие аннотаций для авторизованного пользователя."""
        user = setup_data['user']
        collection = setup_data['collection']
        city1 = setup_data['city1']

        # Добавляем посещение
        VisitedCity.objects.create(
            user=user, city=city1, rating=5, has_magnet=True, is_first_visit=True
        )

        cities = get_all_cities_from_collection(collection.id, user)
        visited_city = cities.filter(id=city1.id).first()

        assert visited_city is not None
        assert hasattr(visited_city, 'is_visited')
        assert hasattr(visited_city, 'visit_dates')
        assert hasattr(visited_city, 'first_visit_date')
        assert hasattr(visited_city, 'last_visit_date')
        assert hasattr(visited_city, 'average_rating')
        assert hasattr(visited_city, 'has_souvenir')
        assert hasattr(visited_city, 'number_of_visits')

    def test_is_visited_true_for_visited_city(self, setup_data: dict[str, Any]) -> None:
        """Проверяет что is_visited=True для посещенного города."""
        user = setup_data['user']
        collection = setup_data['collection']
        city1 = setup_data['city1']

        VisitedCity.objects.create(user=user, city=city1, rating=3, is_first_visit=True)

        cities = get_all_cities_from_collection(collection.id, user)
        visited_city = cities.get(id=city1.id)

        assert visited_city.is_visited is True  # type: ignore[attr-defined]

    def test_is_visited_false_for_not_visited_city(self, setup_data: dict[str, Any]) -> None:
        """Проверяет что is_visited=False для непосещенного города."""
        user = setup_data['user']
        collection = setup_data['collection']
        city2 = setup_data['city2']

        cities = get_all_cities_from_collection(collection.id, user)
        not_visited_city = cities.get(id=city2.id)

        assert not_visited_city.is_visited is False  # type: ignore[attr-defined]

    def test_filters_only_collection_cities(self, setup_data: dict[str, Any]) -> None:
        """Проверяет что возвращаются только города из коллекции."""
        collection = setup_data['collection']
        city3 = setup_data['city3']

        cities = get_all_cities_from_collection(collection.id)

        assert cities.count() == 2
        assert not cities.filter(id=city3.id).exists()

    def test_empty_collection(self, setup_data: dict[str, Any]) -> None:
        """Проверяет работу с пустой коллекцией."""
        empty_collection = Collection.objects.create(title='Пустая')

        cities = get_all_cities_from_collection(empty_collection.id)

        assert cities.count() == 0

    def test_collection_does_not_exist_raises_error(self) -> None:
        """Проверяет что несуществующая коллекция вызывает ошибку."""
        with pytest.raises(Collection.DoesNotExist):
            get_all_cities_from_collection(999999)

    def test_has_souvenir_true_when_magnet_exists(self, setup_data: dict[str, Any]) -> None:
        """Проверяет что has_souvenir=True когда есть магнит."""
        user = setup_data['user']
        collection = setup_data['collection']
        city1 = setup_data['city1']

        VisitedCity.objects.create(
            user=user, city=city1, has_magnet=True, rating=5, is_first_visit=True
        )

        cities = get_all_cities_from_collection(collection.id, user)
        visited_city = cities.get(id=city1.id)

        assert visited_city.has_souvenir is True  # type: ignore[attr-defined]

    def test_number_of_visits_counts_correctly(self, setup_data: dict[str, Any]) -> None:
        """Проверяет что number_of_visits подсчитывается правильно."""
        user = setup_data['user']
        collection = setup_data['collection']
        city1 = setup_data['city1']

        VisitedCity.objects.create(user=user, city=city1, rating=3, is_first_visit=True)
        VisitedCity.objects.create(user=user, city=city1, rating=3, is_first_visit=False)
        VisitedCity.objects.create(user=user, city=city1, rating=3, is_first_visit=False)

        cities = get_all_cities_from_collection(collection.id, user)
        visited_city = cities.get(id=city1.id)

        assert visited_city.number_of_visits == 3  # type: ignore[attr-defined]
