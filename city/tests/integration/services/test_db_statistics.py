"""
Integration тесты для статистических функций DB Services (city/services/db.py).

Тестируются функции:
- get_number_of_* (подсчёт городов, посещений)
- get_rank_* (рейтинги городов)
- get_neighboring_cities_* (соседние города в рейтинге)
- get_number_of_users_who_visit_city
"""

from datetime import date
from typing import Any

import pytest
from django.contrib.auth.models import User

from city.models import City, VisitedCity
from city.services.db import (
    get_number_of_cities,
    get_number_of_cities_in_country,
    get_number_of_cities_in_region_by_city,
    get_number_of_new_visited_cities,
    get_number_of_visited_cities,
    get_number_of_not_visited_cities,
    get_number_of_users_who_visit_city,
    get_rank_by_visits_of_city,
    get_rank_by_users_of_city,
    get_rank_by_visits_of_city_in_region,
    get_rank_by_users_of_city_in_region,
    get_neighboring_cities_by_visits_rank,
    get_neighboring_cities_by_users_rank,
    get_neighboring_cities_in_region_by_visits_rank,
    get_neighboring_cities_in_region_by_users_rank,
    get_number_of_total_visited_cities_by_year,
    get_number_of_new_visited_cities_by_year,
)
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType


@pytest.fixture
def setup_countries(django_user_model: Any) -> dict[str, Any]:
    """Создание базовой структуры стран и пользователей."""
    part = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name='Восточная Европа', part_of_the_world=part)
    
    country_ru = Country.objects.create(
        name='Россия', code='RU', fullname='Российская Федерация', location=location
    )
    country_kz = Country.objects.create(
        name='Казахстан', code='KZ', fullname='Республика Казахстан', location=location
    )
    
    user1 = django_user_model.objects.create_user(username='user1', password='pass')
    user2 = django_user_model.objects.create_user(username='user2', password='pass')
    
    return {
        'country_ru': country_ru,
        'country_kz': country_kz,
        'user1': user1,
        'user2': user2,
        'location': location,
    }


@pytest.fixture
def setup_cities(setup_countries: dict[str, Any]) -> dict[str, Any]:
    """Создание городов и регионов."""
    country_ru = setup_countries['country_ru']
    country_kz = setup_countries['country_kz']
    
    # Регионы России
    region_type = RegionType.objects.create(title='Область')
    area_ru = Area.objects.create(country=country_ru, title='Центральный')
    
    region_moscow = Region.objects.create(
        title='Московская', country=country_ru, type=region_type,
        area=area_ru, iso3166='MOS', full_name='Московская область'
    )
    region_spb = Region.objects.create(
        title='Ленинградская', country=country_ru, type=region_type,
        area=area_ru, iso3166='LEN', full_name='Ленинградская область'
    )
    
    # Регион Казахстана
    area_kz = Area.objects.create(country=country_kz, title='Центральный КЗ')
    region_kz = Region.objects.create(
        title='Алматинская', country=country_kz, type=region_type,
        area=area_kz, iso3166='ALM', full_name='Алматинская область'
    )
    
    # Города России
    moscow = City.objects.create(
        title='Москва', country=country_ru, region=region_moscow,
        coordinate_width=55.75, coordinate_longitude=37.62
    )
    spb = City.objects.create(
        title='Санкт-Петербург', country=country_ru, region=region_spb,
        coordinate_width=59.93, coordinate_longitude=30.34
    )
    kazan = City.objects.create(
        title='Казань', country=country_ru, region=region_moscow,
        coordinate_width=55.79, coordinate_longitude=49.12
    )
    
    # Город Казахстана
    almaty = City.objects.create(
        title='Алматы', country=country_kz, region=region_kz,
        coordinate_width=43.25, coordinate_longitude=76.95
    )
    
    return {
        **setup_countries,
        'moscow': moscow,
        'spb': spb,
        'kazan': kazan,
        'almaty': almaty,
        'region_moscow': region_moscow,
        'region_spb': region_spb,
        'region_kz': region_kz,
    }


@pytest.mark.django_db
@pytest.mark.integration
class TestNumberOfCitiesFunctions:
    """Тесты функций подсчёта городов."""

    def test_get_number_of_cities_all(self, setup_cities: dict[str, Any]) -> None:
        """Подсчёт всех городов."""
        count = get_number_of_cities()
        
        assert count == 4  # moscow, spb, kazan, almaty

    def test_get_number_of_cities_by_country(self, setup_cities: dict[str, Any]) -> None:
        """Подсчёт городов в конкретной стране."""
        count_ru = get_number_of_cities(country_code='RU')
        count_kz = get_number_of_cities(country_code='KZ')
        
        assert count_ru == 3  # moscow, spb, kazan
        assert count_kz == 1  # almaty

    def test_get_number_of_cities_in_country(self, setup_cities: dict[str, Any]) -> None:
        """Подсчёт городов в стране по коду."""
        count = get_number_of_cities_in_country('RU')
        
        assert count == 3

    def test_get_number_of_cities_in_region_by_city(
        self, setup_cities: dict[str, Any]
    ) -> None:
        """Подсчёт городов в регионе по ID города."""
        moscow = setup_cities['moscow']
        kazan = setup_cities['kazan']  # В том же регионе
        
        count = get_number_of_cities_in_region_by_city(moscow.id)
        
        assert count == 2  # moscow и kazan в одном регионе

    def test_get_number_of_cities_in_region_nonexistent_city(self) -> None:
        """Подсчёт для несуществующего города."""
        count = get_number_of_cities_in_region_by_city(99999)
        
        assert count == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestVisitedCitiesCountFunctions:
    """Тесты функций подсчёта посещённых городов."""

    def test_get_number_of_new_visited_cities_no_visits(
        self, setup_cities: dict[str, Any]
    ) -> None:
        """Подсчёт уникальных городов, если посещений нет."""
        user1 = setup_cities['user1']
        
        count = get_number_of_new_visited_cities(user1.id)
        
        assert count == 0

    def test_get_number_of_new_visited_cities_with_visits(
        self, setup_cities: dict[str, Any]
    ) -> None:
        """Подсчёт уникальных городов с посещениями."""
        user1 = setup_cities['user1']
        moscow = setup_cities['moscow']
        spb = setup_cities['spb']
        
        # Создаём посещения (первые)
        VisitedCity.objects.create(
            user=user1, city=moscow, date_of_visit=date(2024, 1, 1),
            rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user1, city=spb, date_of_visit=date(2024, 2, 1),
            rating=4, is_first_visit=True
        )
        # Повторное посещение Москвы
        VisitedCity.objects.create(
            user=user1, city=moscow, date_of_visit=date(2024, 3, 1),
            rating=5, is_first_visit=False
        )
        
        count = get_number_of_new_visited_cities(user1.id)
        
        assert count == 2  # Только уникальные города

    def test_get_number_of_new_visited_cities_by_country(
        self, setup_cities: dict[str, Any]
    ) -> None:
        """Подсчёт уникальных городов в конкретной стране."""
        user1 = setup_cities['user1']
        moscow = setup_cities['moscow']
        almaty = setup_cities['almaty']
        
        VisitedCity.objects.create(
            user=user1, city=moscow, rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user1, city=almaty, rating=4, is_first_visit=True
        )
        
        count_ru = get_number_of_new_visited_cities(user1.id, country_code='RU')
        count_kz = get_number_of_new_visited_cities(user1.id, country_code='KZ')
        
        assert count_ru == 1
        assert count_kz == 1

    def test_get_number_of_visited_cities_with_repeats(
        self, setup_cities: dict[str, Any]
    ) -> None:
        """Подсчёт всех посещений (включая повторные)."""
        user1 = setup_cities['user1']
        moscow = setup_cities['moscow']
        
        VisitedCity.objects.create(
            user=user1, city=moscow, date_of_visit=date(2024, 1, 1),
            rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user1, city=moscow, date_of_visit=date(2024, 2, 1),
            rating=4, is_first_visit=False
        )
        VisitedCity.objects.create(
            user=user1, city=moscow, date_of_visit=date(2024, 3, 1),
            rating=5, is_first_visit=False
        )
        
        count = get_number_of_visited_cities(user1.id)
        
        assert count == 3  # Все посещения

    def test_get_number_of_not_visited_cities(self, setup_cities: dict[str, Any]) -> None:
        """Подсчёт непосещённых городов."""
        user1 = setup_cities['user1']
        moscow = setup_cities['moscow']
        
        # Всего 4 города, посетили 1
        VisitedCity.objects.create(
            user=user1, city=moscow, rating=5, is_first_visit=True
        )
        
        count = get_number_of_not_visited_cities(user1.id)
        
        assert count == 3  # 4 - 1 = 3


@pytest.mark.django_db
@pytest.mark.integration
class TestYearlyStatisticsFunctions:
    """Тесты функций статистики по годам."""

    def test_get_number_of_total_visited_cities_by_year(
        self, setup_cities: dict[str, Any]
    ) -> None:
        """Подсчёт всех посещений за год."""
        user1 = setup_cities['user1']
        moscow = setup_cities['moscow']
        spb = setup_cities['spb']
        
        VisitedCity.objects.create(
            user=user1, city=moscow, date_of_visit=date(2023, 1, 1),
            rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user1, city=moscow, date_of_visit=date(2023, 6, 1),
            rating=4, is_first_visit=False
        )
        VisitedCity.objects.create(
            user=user1, city=spb, date_of_visit=date(2023, 12, 1),
            rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user1, city=moscow, date_of_visit=date(2024, 1, 1),
            rating=5, is_first_visit=False
        )
        
        count_2023 = get_number_of_total_visited_cities_by_year(user1.id, 2023)
        count_2024 = get_number_of_total_visited_cities_by_year(user1.id, 2024)
        
        assert count_2023 == 3  # Все посещения в 2023
        assert count_2024 == 1  # Одно посещение в 2024

    def test_get_number_of_new_visited_cities_by_year(
        self, setup_cities: dict[str, Any]
    ) -> None:
        """Подсчёт новых городов за год."""
        user1 = setup_cities['user1']
        moscow = setup_cities['moscow']
        spb = setup_cities['spb']
        
        VisitedCity.objects.create(
            user=user1, city=moscow, date_of_visit=date(2023, 1, 1),
            rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user1, city=spb, date_of_visit=date(2023, 12, 1),
            rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user1, city=moscow, date_of_visit=date(2024, 1, 1),
            rating=5, is_first_visit=False  # Повторное посещение
        )
        
        count_2023 = get_number_of_new_visited_cities_by_year(user1.id, 2023)
        count_2024 = get_number_of_new_visited_cities_by_year(user1.id, 2024)
        
        assert count_2023 == 2  # Два новых города
        assert count_2024 == 0  # Нет новых городов


@pytest.mark.django_db
@pytest.mark.integration
class TestUserVisitStatistics:
    """Тесты статистики посещений пользователей."""

    def test_get_number_of_users_who_visit_city(
        self, setup_cities: dict[str, Any]
    ) -> None:
        """Подсчёт количества пользователей, посетивших город."""
        user1 = setup_cities['user1']
        user2 = setup_cities['user2']
        moscow = setup_cities['moscow']
        
        VisitedCity.objects.create(
            user=user1, city=moscow, rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user2, city=moscow, rating=4, is_first_visit=True
        )
        # Повторное посещение не должно учитываться
        VisitedCity.objects.create(
            user=user1, city=moscow, rating=5, is_first_visit=False
        )
        
        count = get_number_of_users_who_visit_city(moscow.id)
        
        assert count == 2  # Два уникальных пользователя


@pytest.mark.django_db
@pytest.mark.integration
class TestRankingFunctions:
    """Тесты функций рейтингов городов."""

    def test_get_rank_by_visits_of_city(self, setup_cities: dict[str, Any]) -> None:
        """Рейтинг города по количеству посещений."""
        user1 = setup_cities['user1']
        user2 = setup_cities['user2']
        moscow = setup_cities['moscow']
        spb = setup_cities['spb']
        kazan = setup_cities['kazan']
        
        # Москва - 5 посещений
        for _ in range(5):
            VisitedCity.objects.create(user=user1, city=moscow, rating=5)
        
        # Питер - 3 посещения
        for _ in range(3):
            VisitedCity.objects.create(user=user2, city=spb, rating=4)
        
        # Казань - 1 посещение
        VisitedCity.objects.create(user=user1, city=kazan, rating=3)
        
        rank_moscow = get_rank_by_visits_of_city(moscow.id)
        rank_spb = get_rank_by_visits_of_city(spb.id)
        rank_kazan = get_rank_by_visits_of_city(kazan.id)
        
        assert rank_moscow == 1  # Больше всего посещений
        assert rank_spb == 2
        assert rank_kazan == 3

    def test_get_rank_by_users_of_city(self, setup_cities: dict[str, Any]) -> None:
        """Рейтинг города по количеству пользователей."""
        user1 = setup_cities['user1']
        user2 = setup_cities['user2']
        moscow = setup_cities['moscow']
        spb = setup_cities['spb']
        
        # Москва - 2 пользователя
        VisitedCity.objects.create(user=user1, city=moscow, rating=5)
        VisitedCity.objects.create(user=user2, city=moscow, rating=4)
        
        # Питер - 1 пользователь
        VisitedCity.objects.create(user=user1, city=spb, rating=5)
        
        rank_moscow = get_rank_by_users_of_city(moscow.id)
        rank_spb = get_rank_by_users_of_city(spb.id)
        
        assert rank_moscow == 1
        assert rank_spb == 2

    def test_get_rank_by_visits_in_region(self, setup_cities: dict[str, Any]) -> None:
        """Рейтинг города в регионе по посещениям."""
        user1 = setup_cities['user1']
        moscow = setup_cities['moscow']
        kazan = setup_cities['kazan']  # В том же регионе
        
        # Москва - 3 посещения
        for _ in range(3):
            VisitedCity.objects.create(user=user1, city=moscow, rating=5)
        
        # Казань - 1 посещение
        VisitedCity.objects.create(user=user1, city=kazan, rating=4)
        
        rank_moscow = get_rank_by_visits_of_city_in_region(moscow.id)
        rank_kazan = get_rank_by_visits_of_city_in_region(kazan.id)
        
        assert rank_moscow == 1
        assert rank_kazan == 2


@pytest.mark.django_db
@pytest.mark.integration
class TestNeighboringCitiesFunctions:
    """Тесты функций получения соседних городов в рейтинге."""

    def test_get_neighboring_cities_by_visits_rank(
        self, setup_cities: dict[str, Any]
    ) -> None:
        """Получение соседних городов по рейтингу посещений."""
        user1 = setup_cities['user1']
        moscow = setup_cities['moscow']
        spb = setup_cities['spb']
        kazan = setup_cities['kazan']
        
        # Создаём посещения для формирования рейтинга
        for _ in range(3):
            VisitedCity.objects.create(user=user1, city=moscow, rating=5)
        for _ in range(2):
            VisitedCity.objects.create(user=user1, city=spb, rating=4)
        VisitedCity.objects.create(user=user1, city=kazan, rating=3)
        
        neighbors = get_neighboring_cities_by_visits_rank(spb.id)
        
        # Должен вернуть список словарей с соседями по рейтингу
        assert isinstance(neighbors, list)
        assert len(neighbors) <= 10

    def test_get_neighboring_cities_nonexistent_city(self) -> None:
        """Соседи для несуществующего города."""
        neighbors = get_neighboring_cities_by_visits_rank(99999)
        
        assert neighbors == []

    def test_get_neighboring_cities_in_region(self, setup_cities: dict[str, Any]) -> None:
        """Получение соседних городов в регионе."""
        user1 = setup_cities['user1']
        moscow = setup_cities['moscow']
        kazan = setup_cities['kazan']  # В том же регионе
        
        VisitedCity.objects.create(user=user1, city=moscow, rating=5)
        VisitedCity.objects.create(user=user1, city=kazan, rating=4)
        
        neighbors = get_neighboring_cities_in_region_by_visits_rank(moscow.id)
        
        assert isinstance(neighbors, list)

