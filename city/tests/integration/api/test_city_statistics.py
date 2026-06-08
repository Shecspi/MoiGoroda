"""
Тесты для эндпоинта /api/city/statistics/<city_id>/ (CityStatisticsController).

Покрывает:
- Успешный ответ со схемой CityStatisticsResponse
- 404 для несуществующего города
- Публичный доступ (без авторизации)
- Корректность рангов и счётчиков на реальных данных
- Структуру списков соседних городов
- Город без региона
- Запрещённые HTTP-методы
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any, cast

import pytest
from django.test import Client
from django.urls import reverse
from rest_framework import status

from city.models import City, VisitedCity
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType

STATISTICS_RESPONSE_KEYS = {
    'number_of_cities_in_country',
    'number_of_cities_in_region',
    'rank_in_country_by_visits',
    'rank_in_country_by_users',
    'rank_in_region_by_visits',
    'rank_in_region_by_users',
    'neighboring_cities_by_rank_in_country_by_users',
    'neighboring_cities_by_rank_in_country_by_visits',
    'neighboring_cities_by_rank_in_region_by_users',
    'neighboring_cities_by_rank_in_region_by_visits',
}

NEIGHBORING_CITY_KEYS = {'id', 'title', 'visits', 'rank'}


def statistics_url(city_id: int) -> str:
    return reverse('api__get_city_statistics', kwargs={'city_id': city_id})


def response_json(response: object) -> dict[str, Any]:
    content = getattr(response, 'content', b'')
    return cast(dict[str, Any], json.loads(content.decode()))


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def setup_countries(django_user_model: Any) -> dict[str, Any]:
    part = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name='Восточная Европа', part_of_the_world=part)

    country_ru = Country.objects.create(
        name='Россия', code='RU', fullname='Российская Федерация', location=location
    )
    country_kz = Country.objects.create(
        name='Казахстан', code='KZ', fullname='Республика Казахстан', location=location
    )

    user1 = django_user_model.objects.create_user(username='stats_user1', password='pass')
    user2 = django_user_model.objects.create_user(username='stats_user2', password='pass')

    return {
        'country_ru': country_ru,
        'country_kz': country_kz,
        'user1': user1,
        'user2': user2,
    }


@pytest.fixture
def setup_cities(setup_countries: dict[str, Any]) -> dict[str, Any]:
    country_ru = setup_countries['country_ru']
    country_kz = setup_countries['country_kz']

    region_type = RegionType.objects.create(title='Область')
    area_ru = Area.objects.create(country=country_ru, title='Центральный')

    region_moscow = Region.objects.create(
        title='Московская',
        country=country_ru,
        type=region_type,
        area=area_ru,
        iso3166='MOS',
        full_name='Московская область',
    )
    region_spb = Region.objects.create(
        title='Ленинградская',
        country=country_ru,
        type=region_type,
        area=area_ru,
        iso3166='LEN',
        full_name='Ленинградская область',
    )

    moscow = City.objects.create(
        title='Москва',
        country=country_ru,
        region=region_moscow,
        coordinate_width=55.75,
        coordinate_longitude=37.62,
    )
    spb = City.objects.create(
        title='Санкт-Петербург',
        country=country_ru,
        region=region_spb,
        coordinate_width=59.93,
        coordinate_longitude=30.34,
    )
    kazan = City.objects.create(
        title='Казань',
        country=country_ru,
        region=region_moscow,
        coordinate_width=55.79,
        coordinate_longitude=49.12,
    )
    city_without_region = City.objects.create(
        title='Севастополь',
        country=country_ru,
        region=None,
        coordinate_width=44.60,
        coordinate_longitude=33.52,
    )
    City.objects.create(
        title='Алматы',
        country=country_kz,
        region=None,
        coordinate_width=43.25,
        coordinate_longitude=76.95,
    )

    return {
        **setup_countries,
        'moscow': moscow,
        'spb': spb,
        'kazan': kazan,
        'city_without_region': city_without_region,
        'region_moscow': region_moscow,
    }


def _seed_visit_rankings(setup_cities: dict[str, Any]) -> None:
    user1 = setup_cities['user1']
    user2 = setup_cities['user2']
    moscow = setup_cities['moscow']
    spb = setup_cities['spb']
    kazan = setup_cities['kazan']

    for day in range(1, 6):
        VisitedCity.objects.create(
            user=user1,
            city=moscow,
            date_of_visit=date(2024, 1, day),
            rating=5,
            is_first_visit=day == 1,
        )
    for day in range(1, 4):
        VisitedCity.objects.create(
            user=user2,
            city=spb,
            date_of_visit=date(2024, 2, day),
            rating=4,
            is_first_visit=day == 1,
        )
    VisitedCity.objects.create(
        user=user1,
        city=kazan,
        date_of_visit=date(2024, 3, 1),
        rating=3,
        is_first_visit=True,
    )
    VisitedCity.objects.create(
        user=user2,
        city=moscow,
        date_of_visit=date(2024, 4, 1),
        rating=5,
        is_first_visit=True,
    )


@pytest.mark.django_db
@pytest.mark.integration
def test_statistics_guest_can_access(client: Client, setup_cities: dict[str, Any]) -> None:
    moscow = setup_cities['moscow']

    response = client.get(statistics_url(moscow.id))

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.integration
def test_statistics_returns_404_for_missing_city(client: Client) -> None:
    response = client.get(statistics_url(999_999))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
def test_statistics_prohibited_methods(
    client: Client, setup_cities: dict[str, Any], method: str
) -> None:
    moscow = setup_cities['moscow']
    client_method = getattr(client, method)

    response = client_method(statistics_url(moscow.id))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
@pytest.mark.integration
def test_statistics_response_contains_expected_fields(
    client: Client, setup_cities: dict[str, Any]
) -> None:
    _seed_visit_rankings(setup_cities)
    moscow = setup_cities['moscow']

    data = response_json(client.get(statistics_url(moscow.id)))

    assert set(data.keys()) == STATISTICS_RESPONSE_KEYS
    assert 'number_of_users_who_visit_city' not in data
    assert 'number_of_visits_all_users' not in data


@pytest.mark.django_db
@pytest.mark.integration
def test_statistics_returns_correct_counts_and_ranks(
    client: Client, setup_cities: dict[str, Any]
) -> None:
    _seed_visit_rankings(setup_cities)
    moscow = setup_cities['moscow']

    data = response_json(client.get(statistics_url(moscow.id)))

    assert data['number_of_cities_in_country'] == 4
    assert data['number_of_cities_in_region'] == 2
    assert data['rank_in_country_by_visits'] == 1
    assert data['rank_in_country_by_users'] == 1
    assert data['rank_in_region_by_visits'] == 1
    assert data['rank_in_region_by_users'] == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_statistics_neighboring_cities_have_expected_shape(
    client: Client, setup_cities: dict[str, Any]
) -> None:
    _seed_visit_rankings(setup_cities)
    moscow = setup_cities['moscow']

    data = response_json(client.get(statistics_url(moscow.id)))

    for key in (
        'neighboring_cities_by_rank_in_country_by_users',
        'neighboring_cities_by_rank_in_country_by_visits',
        'neighboring_cities_by_rank_in_region_by_users',
        'neighboring_cities_by_rank_in_region_by_visits',
    ):
        neighbors = data[key]
        assert isinstance(neighbors, list)
        assert len(neighbors) <= 10
        for item in neighbors:
            assert set(item.keys()) == NEIGHBORING_CITY_KEYS
            assert isinstance(item['id'], int)
            assert isinstance(item['title'], str)
            assert isinstance(item['visits'], int)
            assert isinstance(item['rank'], int)


@pytest.mark.django_db
@pytest.mark.integration
def test_statistics_includes_current_city_in_country_neighbors(
    client: Client, setup_cities: dict[str, Any]
) -> None:
    _seed_visit_rankings(setup_cities)
    moscow = setup_cities['moscow']

    data = response_json(client.get(statistics_url(moscow.id)))
    neighbor_ids = {item['id'] for item in data['neighboring_cities_by_rank_in_country_by_visits']}

    assert moscow.id in neighbor_ids


@pytest.mark.django_db
@pytest.mark.integration
def test_statistics_city_without_region_returns_200(
    client: Client, setup_cities: dict[str, Any]
) -> None:
    city = setup_cities['city_without_region']

    response = client.get(statistics_url(city.id))

    assert response.status_code == status.HTTP_200_OK
    data = response_json(response)
    assert set(data.keys()) == STATISTICS_RESPONSE_KEYS
    assert data['number_of_cities_in_country'] == 4


@pytest.mark.django_db
@pytest.mark.integration
def test_statistics_spb_rank_in_country_by_visits(
    client: Client, setup_cities: dict[str, Any]
) -> None:
    _seed_visit_rankings(setup_cities)
    spb = setup_cities['spb']

    data = response_json(client.get(statistics_url(spb.id)))

    assert data['rank_in_country_by_visits'] == 2
    assert data['rank_in_country_by_users'] == 2
