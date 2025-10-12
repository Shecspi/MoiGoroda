"""
Интеграционные тесты для repository приложения country.
"""

from datetime import date
from typing import Any

import pytest
from django.contrib.auth.models import User

from city.models import City, VisitedCity
from country.models import Country
from country.repository import (
    get_countries_with_visited_city,
    get_countries_with_visited_city_in_year,
    get_countries_with_new_visited_city_in_year,
    get_list_of_countries_with_visited_regions,
)
from region.models import Region


@pytest.mark.django_db
@pytest.mark.integration
class TestGetCountriesWithVisitedCity:
    """Интеграционные тесты для get_countries_with_visited_city."""

    @pytest.fixture
    def setup_data(self, user: User, region_type: Any) -> dict[str, Any]:
        """Создает данные для тестов."""
        russia = Country.objects.create(name='Россия', code='RU')
        germany = Country.objects.create(name='Германия', code='DE')

        region_ru = Region.objects.create(
            title='Москва',
            country=russia,
            type=region_type,
            iso3166='RU-MOW-T',
            full_name='г. Москва',
        )
        region_de = Region.objects.create(
            title='Берлин', country=germany, type=region_type, iso3166='DE-BE-T', full_name='Берлин'
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
        VisitedCity.objects.create(user=user, city=berlin, rating=4, is_first_visit=True)

        return {
            'user': user,
            'russia': russia,
            'germany': germany,
            'moscow': moscow,
            'berlin': berlin,
        }

    def test_returns_countries_with_visited_cities(self, setup_data: dict[str, Any]) -> None:
        """Проверяет что возвращаются страны с посещенными городами."""
        user = setup_data['user']

        countries = get_countries_with_visited_city(user.id)

        assert countries.count() == 2

    def test_annotates_with_total_cities(self, setup_data: dict[str, Any]) -> None:
        """Проверяет аннотацию total_cities."""
        user = setup_data['user']

        countries = get_countries_with_visited_city(user.id)
        country = countries.first()

        assert country is not None
        assert hasattr(country, 'total_cities')

    def test_annotates_with_visited_cities(self, setup_data: dict[str, Any]) -> None:
        """Проверяет аннотацию visited_cities."""
        user = setup_data['user']

        countries = get_countries_with_visited_city(user.id)
        country = countries.first()

        assert country is not None
        assert hasattr(country, 'visited_cities')

    def test_orders_by_visited_cities_desc(self, setup_data: dict[str, Any]) -> None:
        """Проверяет сортировку по убыванию visited_cities."""
        user = setup_data['user']
        russia = setup_data['russia']

        # Добавляем еще один город в Россию
        region = setup_data['moscow'].region
        spb = City.objects.create(
            title='Санкт-Петербург',
            region=region,
            country=russia,
            coordinate_width='59.9343',
            coordinate_longitude='30.3351',
        )
        VisitedCity.objects.create(user=user, city=spb, rating=5, is_first_visit=True)

        countries = get_countries_with_visited_city(user.id)

        # Россия должна быть первой (2 посещенных города)
        assert countries.first() == russia


@pytest.mark.django_db
@pytest.mark.integration
class TestGetCountriesWithVisitedCityInYear:
    """Интеграционные тесты для get_countries_with_visited_city_in_year."""

    def test_filters_visits_by_year(self, user: User, region_type: Any) -> None:
        """Проверяет фильтрацию посещений по году."""
        russia = Country.objects.create(name='Россия', code='RU')
        region = Region.objects.create(
            title='Москва',
            country=russia,
            type=region_type,
            iso3166='RU-2024',
            full_name='г. Москва',
        )

        moscow = City.objects.create(
            title='Москва',
            region=region,
            country=russia,
            coordinate_width='55.7558',
            coordinate_longitude='37.6173',
        )

        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2023, 5, 1), rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 6, 1), rating=4, is_first_visit=False
        )

        countries_2024 = get_countries_with_visited_city_in_year(user.id, 2024)
        countries_2023 = get_countries_with_visited_city_in_year(user.id, 2023)

        assert countries_2024.count() == 1
        assert countries_2023.count() == 1


@pytest.mark.django_db
@pytest.mark.integration
class TestGetCountriesWithNewVisitedCityInYear:
    """Интеграционные тесты для get_countries_with_new_visited_city_in_year."""

    def test_filters_only_first_visits(self, user: User, region_type: Any) -> None:
        """Проверяет что учитываются только первые посещения."""
        russia = Country.objects.create(name='Россия', code='RU')
        region = Region.objects.create(
            title='Москва',
            country=russia,
            type=region_type,
            iso3166='RU-2025',
            full_name='г. Москва',
        )

        moscow = City.objects.create(
            title='Москва',
            region=region,
            country=russia,
            coordinate_width='55.7558',
            coordinate_longitude='37.6173',
        )

        # Первое посещение в 2023
        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2023, 5, 1), rating=5, is_first_visit=True
        )
        # Повторное посещение в 2024
        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 6, 1), rating=4, is_first_visit=False
        )

        countries_2024 = get_countries_with_new_visited_city_in_year(user.id, 2024)
        countries_2023 = get_countries_with_new_visited_city_in_year(user.id, 2023)

        # В 2024 не было новых посещений
        assert countries_2024.count() == 0
        # В 2023 было первое посещение
        assert countries_2023.count() == 1


@pytest.mark.django_db
@pytest.mark.integration
class TestGetListOfCountriesWithVisitedRegions:
    """Интеграционные тесты для get_list_of_countries_with_visited_regions."""

    def test_returns_countries_with_visited_regions(self, user: User, region_type: Any) -> None:
        """Проверяет что возвращаются страны с посещенными регионами."""
        russia = Country.objects.create(name='Россия', code='RU')
        region1 = Region.objects.create(
            title='Москва',
            country=russia,
            type=region_type,
            iso3166='RU-REG',
            full_name='г. Москва',
        )
        region2 = Region.objects.create(
            title='Санкт-Петербург',
            country=russia,
            type=region_type,
            iso3166='RU-SPE-R',
            full_name='г. Санкт-Петербург',
        )

        moscow = City.objects.create(
            title='Москва',
            region=region1,
            country=russia,
            coordinate_width='55.7558',
            coordinate_longitude='37.6173',
        )
        spb = City.objects.create(
            title='Санкт-Петербург',
            region=region2,
            country=russia,
            coordinate_width='59.9343',
            coordinate_longitude='30.3351',
        )

        VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=True)
        VisitedCity.objects.create(user=user, city=spb, rating=4, is_first_visit=True)

        countries = get_list_of_countries_with_visited_regions(user.id)

        assert countries.count() == 1
        assert countries.first() == russia

    def test_filters_by_year(self, user: User, region_type: Any) -> None:
        """Проверяет фильтрацию по году."""
        russia = Country.objects.create(name='Россия', code='RU')
        region = Region.objects.create(
            title='Москва',
            country=russia,
            type=region_type,
            iso3166='RU-YEAR',
            full_name='г. Москва',
        )

        moscow = City.objects.create(
            title='Москва',
            region=region,
            country=russia,
            coordinate_width='55.7558',
            coordinate_longitude='37.6173',
        )

        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2023, 5, 1), rating=5, is_first_visit=True
        )

        countries_2023 = get_list_of_countries_with_visited_regions(user.id, year=2023)
        countries_2024 = get_list_of_countries_with_visited_regions(user.id, year=2024)

        assert countries_2023.count() == 1
        assert countries_2024.count() == 0
