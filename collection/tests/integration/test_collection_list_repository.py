"""
Интеграционные тесты оптимизированных методов репозитория списка коллекций.
"""

from typing import Any

import pytest
from django.contrib.auth.models import User

from city.models import City, VisitedCity
from collection.models import Collection
from collection.repository import (
    COLLECTION_LIST_PREVIEW_CITIES_LIMIT,
    CollectionRepository,
)
from country.models import Country
from region.models import Region


@pytest.fixture
def collection_list_setup(region_type: Any) -> dict[str, Any]:
    """Коллекции с разным прогрессом и большим числом городов."""
    user = User.objects.create_user(username='list_user', password='testpass')
    country = Country.objects.create(name='Россия', code='RU')
    region = Region.objects.create(
        title='Москва', country=country, type=region_type, iso3166='RU-MOW', full_name='Москва'
    )

    cities = City.objects.bulk_create(
        [
            City(
                title=f'Город {index:03d}',
                region=region,
                country=country,
                coordinate_width=55.0 + index * 0.01,
                coordinate_longitude=37.0 + index * 0.01,
            )
            for index in range(15)
        ]
    )

    empty_collection = Collection.objects.create(title='Пустая')
    started_collection = Collection.objects.create(title='Начатая')
    finished_collection = Collection.objects.create(title='Завершённая')
    large_collection = Collection.objects.create(title='Большая')

    started_collection.city.set(cities[:5])
    finished_collection.city.set(cities[:3])
    large_collection.city.set(cities)

    VisitedCity.objects.create(user=user, city=cities[0], rating=3, is_first_visit=True)
    VisitedCity.objects.create(user=user, city=cities[1], rating=3, is_first_visit=True)
    VisitedCity.objects.create(user=user, city=cities[2], rating=3, is_first_visit=True)

    return {
        'user': user,
        'cities': cities,
        'empty_collection': empty_collection,
        'started_collection': started_collection,
        'finished_collection': finished_collection,
        'large_collection': large_collection,
    }


@pytest.mark.django_db
@pytest.mark.integration
def test_get_collection_list_statistics_for_authenticated_user(
    collection_list_setup: dict[str, Any],
) -> None:
    repository = CollectionRepository()
    user = collection_list_setup['user']
    stats = repository.get_collection_list_statistics(user)

    assert stats['qty_of_collections'] == 4
    assert stats['qty_of_started_collections'] == 3
    assert stats['qty_of_finished_collections'] == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_empty_collection_is_not_counted_as_finished(
    collection_list_setup: dict[str, Any],
) -> None:
    """Пустая коллекция не должна попадать в qty_of_finished_collections."""
    repository = CollectionRepository()
    user = collection_list_setup['user']

    stats = repository.get_collection_list_statistics(user)

    assert collection_list_setup['empty_collection'].city.count() == 0
    assert stats['qty_of_finished_collections'] == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_city_without_visitedcity_records_counts_as_unvisited(
    collection_list_setup: dict[str, Any],
) -> None:
    """
    Город без единой записи в VisitedCity (никем не посещён) — непосещённый для пользователя.

    Проверяет, что exclude по M2M не «проглатывает» города без связанных VisitedCity.
    """
    repository = CollectionRepository()
    user = collection_list_setup['user']
    cities = collection_list_setup['cities']

    assert not VisitedCity.objects.filter(city=cities[4]).exists()

    collection = Collection.objects.create(title='Частично с «мёртвым» городом')
    collection.city.set([cities[0], cities[4]])

    stats = repository.get_collection_list_statistics(user)

    assert stats['qty_of_collections'] == 5
    assert stats['qty_of_started_collections'] == 4
    assert stats['qty_of_finished_collections'] == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_finished_when_user_visited_all_cities_including_never_visited_by_others(
    region_type: Any,
) -> None:
    """Коллекция завершена, если пользователь посетил все города, даже «пустые» в VisitedCity."""
    repository = CollectionRepository()
    user = User.objects.create_user(username='finished_user', password='testpass')
    country = Country.objects.create(name='Россия', code='RU')
    region = Region.objects.create(
        title='Москва', country=country, type=region_type, iso3166='RU-MOW', full_name='Москва'
    )
    visited_city = City.objects.create(
        title='Посещённый',
        region=region,
        country=country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )
    orphan_city = City.objects.create(
        title='Без посещений в БД',
        region=region,
        country=country,
        coordinate_width=56.0,
        coordinate_longitude=38.0,
    )
    collection = Collection.objects.create(title='Полная')
    collection.city.set([visited_city, orphan_city])

    VisitedCity.objects.create(user=user, city=visited_city, rating=3, is_first_visit=True)
    VisitedCity.objects.create(user=user, city=orphan_city, rating=3, is_first_visit=True)
    assert VisitedCity.objects.filter(city=orphan_city).count() == 1

    stats = repository.get_collection_list_statistics(user)

    assert stats['qty_of_finished_collections'] == 1
    assert stats['qty_of_started_collections'] == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_get_collection_list_statistics_for_guest() -> None:
    repository = CollectionRepository()
    Collection.objects.create(title='Гостевая')
    stats = repository.get_collection_list_statistics(None)

    assert stats == {
        'qty_of_collections': 1,
        'qty_of_started_collections': 0,
        'qty_of_finished_collections': 0,
    }


@pytest.mark.django_db
@pytest.mark.integration
def test_attach_preview_cities_limits_cities_and_marks_visited(
    collection_list_setup: dict[str, Any],
) -> None:
    repository = CollectionRepository()
    user = collection_list_setup['user']
    large_collection = collection_list_setup['large_collection']

    repository.attach_preview_cities([large_collection], user=user)

    assert len(large_collection.preview_cities) == COLLECTION_LIST_PREVIEW_CITIES_LIMIT
    assert large_collection.preview_cities[0].title == 'Город 000'
    assert large_collection.preview_cities[0].is_visited is True
    assert large_collection.preview_cities[-1].title == 'Город 009'


@pytest.mark.django_db
@pytest.mark.integration
def test_attach_preview_cities_for_guest_marks_all_as_not_visited(
    collection_list_setup: dict[str, Any],
) -> None:
    repository = CollectionRepository()
    started_collection = collection_list_setup['started_collection']

    repository.attach_preview_cities([started_collection], user=None)

    assert all(not city.is_visited for city in started_collection.preview_cities)
