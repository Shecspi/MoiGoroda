"""
Интеграционные тесты для фильтров приложения collection.
"""

from typing import Any

import pytest
from django.contrib.auth.models import User

from city.models import City, VisitedCity
from collection.filter import apply_filter_to_queryset, filter_visited, filter_not_visited
from collection.services import get_all_cities_from_collection
from collection.models import Collection
from country.models import Country
from region.models import Region


@pytest.mark.django_db
@pytest.mark.integration
class TestFilterIntegration:
    """Интеграционные тесты для фильтров с реальными данными."""

    @pytest.fixture
    def setup_data(self, region_type: Any) -> dict[str, Any]:
        """Создает данные для тестов."""
        user = User.objects.create_user(username='testuser', password='testpass')
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

        collection = Collection.objects.create(title='Тестовая коллекция')
        collection.city.set([city1, city2, city3])

        # Посещаем только Москву
        VisitedCity.objects.create(user=user, city=city1, rating=3, is_first_visit=True)

        return {
            'user': user,
            'collection': collection,
            'city1': city1,
            'city2': city2,
            'city3': city3,
        }

    def test_filter_visited_returns_only_visited_cities(self, setup_data: dict[str, Any]) -> None:
        """Проверяет что filter_visited возвращает только посещенные города."""
        user = setup_data['user']
        collection = setup_data['collection']

        cities = get_all_cities_from_collection(collection.id, user)
        filtered_cities = filter_visited(cities)

        assert filtered_cities.count() == 1
        assert filtered_cities.first().title == 'Москва'  # type: ignore[union-attr]

    def test_filter_not_visited_returns_only_not_visited_cities(
        self, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет что filter_not_visited возвращает только непосещенные города."""
        user = setup_data['user']
        collection = setup_data['collection']

        cities = get_all_cities_from_collection(collection.id, user)
        filtered_cities = filter_not_visited(cities)

        assert filtered_cities.count() == 2

    def test_apply_filter_with_visited_filter(self, setup_data: dict[str, Any]) -> None:
        """Проверяет apply_filter_to_queryset с фильтром 'visited'."""
        user = setup_data['user']
        collection = setup_data['collection']

        cities = get_all_cities_from_collection(collection.id, user)
        filtered_cities = apply_filter_to_queryset(cities, 'visited')

        assert filtered_cities.count() == 1

    def test_apply_filter_with_not_visited_filter(self, setup_data: dict[str, Any]) -> None:
        """Проверяет apply_filter_to_queryset с фильтром 'not_visited'."""
        user = setup_data['user']
        collection = setup_data['collection']

        cities = get_all_cities_from_collection(collection.id, user)
        filtered_cities = apply_filter_to_queryset(cities, 'not_visited')

        assert filtered_cities.count() == 2

    def test_filter_with_no_visited_cities(self, setup_data: dict[str, Any]) -> None:
        """Проверяет фильтр когда нет посещенных городов."""
        # Создаем нового пользователя без посещений
        new_user = User.objects.create_user(username='newuser', password='testpass')
        collection = setup_data['collection']

        cities = get_all_cities_from_collection(collection.id, new_user)
        filtered_cities = filter_visited(cities)

        assert filtered_cities.count() == 0

    def test_filter_with_all_cities_visited(self, setup_data: dict[str, Any]) -> None:
        """Проверяет фильтр когда все города посещены."""
        user = setup_data['user']
        collection = setup_data['collection']
        city2 = setup_data['city2']
        city3 = setup_data['city3']

        # Посещаем оставшиеся города
        VisitedCity.objects.create(user=user, city=city2, rating=3, is_first_visit=True)
        VisitedCity.objects.create(user=user, city=city3, rating=3, is_first_visit=True)

        cities = get_all_cities_from_collection(collection.id, user)
        filtered_cities = filter_not_visited(cities)

        assert filtered_cities.count() == 0
