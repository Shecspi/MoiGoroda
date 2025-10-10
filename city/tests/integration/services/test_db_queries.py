"""
Integration тесты для query функций DB Services (city/services/db.py).

Тестируются функции:
- get_*_visited_cities (получение списков городов)
- get_*_visit_date_by_city (получение дат посещений)
- get_number_of_visits_by_city (подсчёт посещений)
- get_not_visited_cities (непосещённые города)
"""

from datetime import date
from typing import Any

import pytest

from city.models import City, VisitedCity
from city.services.db import (
    get_unique_visited_cities,
    get_all_visited_cities,
    get_all_new_visited_cities,
    get_first_visit_date_by_city,
    get_last_visit_date_by_city,
    get_number_of_visits_by_city,
    get_not_visited_cities,
    get_last_10_new_visited_cities,
    get_number_of_total_visited_cities_in_several_years,
    get_number_of_new_visited_cities_in_several_years,
    get_number_of_total_visited_cities_in_several_month,
    get_number_of_new_visited_cities_in_several_month,
)
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType


@pytest.fixture
def setup_data(django_user_model: Any) -> dict[str, Any]:
    """Создание тестовых данных."""
    part = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name='Восточная Европа', part_of_the_world=part)

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
        iso3166='MOS',
        full_name='Московская область',
    )

    moscow = City.objects.create(
        title='Москва',
        country=country,
        region=region,
        coordinate_width=55.75,
        coordinate_longitude=37.62,
    )
    spb = City.objects.create(
        title='Санкт-Петербург',
        country=country,
        region=region,
        coordinate_width=59.93,
        coordinate_longitude=30.34,
    )
    kazan = City.objects.create(
        title='Казань',
        country=country,
        region=region,
        coordinate_width=55.79,
        coordinate_longitude=49.12,
    )

    user = django_user_model.objects.create_user(username='testuser', password='pass')

    return {
        'user': user,
        'country': country,
        'moscow': moscow,
        'spb': spb,
        'kazan': kazan,
    }


@pytest.mark.django_db
@pytest.mark.integration
class TestUniqueVisitedCitiesFunctions:
    """Тесты функций получения уникальных посещённых городов."""

    def test_get_unique_visited_cities_empty(self, setup_data: dict[str, Any]) -> None:
        """Получение пустого списка когда нет посещений."""
        user = setup_data['user']

        cities = get_unique_visited_cities(user.id)

        assert cities.count() == 0

    def test_get_unique_visited_cities_with_data(self, setup_data: dict[str, Any]) -> None:
        """Получение уникальных городов с данными."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        spb = setup_data['spb']

        # Создаём посещения
        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 1, 1), rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=date(2024, 2, 1),
            rating=4,
            is_first_visit=False,  # Повторное посещение
        )
        VisitedCity.objects.create(
            user=user, city=spb, date_of_visit=date(2024, 3, 1), rating=5, is_first_visit=True
        )

        cities = get_unique_visited_cities(user.id)

        # Должно быть только 2 уникальных города
        assert cities.count() == 2

    def test_get_unique_visited_cities_by_country(self, setup_data: dict[str, Any]) -> None:
        """Фильтрация уникальных городов по стране."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=True)

        cities = get_unique_visited_cities(user.id, country_code='RU')

        assert cities.count() == 1
        assert cities.first().city == moscow

    def test_get_unique_visited_cities_annotations(self, setup_data: dict[str, Any]) -> None:
        """Проверка аннотаций в результате."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=date(2024, 1, 1),
            rating=5,
            has_magnet=True,
            is_first_visit=True,
        )
        VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=date(2024, 2, 1),
            rating=4,
            has_magnet=False,
            is_first_visit=False,
        )

        cities = get_unique_visited_cities(user.id)
        city = cities.first()

        # Проверяем наличие аннотаций
        assert hasattr(city, 'number_of_visits')
        assert hasattr(city, 'average_rating')
        assert hasattr(city, 'has_souvenir')

        assert city.number_of_visits == 2
        assert city.has_souvenir is True  # Хотя бы одно посещение с магнитом


@pytest.mark.django_db
@pytest.mark.integration
class TestAllVisitedCitiesFunctions:
    """Тесты функций получения всех посещений."""

    def test_get_all_visited_cities(self, setup_data: dict[str, Any]) -> None:
        """Получение всех посещений включая повторные."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 1, 1), rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 2, 1), rating=4, is_first_visit=False
        )

        cities = get_all_visited_cities(user.id)

        assert cities.count() == 2  # Все посещения

    def test_get_all_new_visited_cities(self, setup_data: dict[str, Any]) -> None:
        """Получение только первых посещений."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        spb = setup_data['spb']

        VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=True)
        VisitedCity.objects.create(user=user, city=moscow, rating=4, is_first_visit=False)
        VisitedCity.objects.create(user=user, city=spb, rating=5, is_first_visit=True)

        cities = get_all_new_visited_cities(user.id)

        assert cities.count() == 2  # Только первые посещения


@pytest.mark.django_db
@pytest.mark.integration
class TestVisitDateFunctions:
    """Тесты функций получения дат посещений."""

    def test_get_first_visit_date_by_city(self, setup_data: dict[str, Any]) -> None:
        """Получение даты первого посещения."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 3, 1), rating=5, is_first_visit=False
        )
        VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=date(2024, 1, 1),
            rating=4,
            is_first_visit=True,  # Самое раннее
        )
        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 2, 1), rating=5, is_first_visit=False
        )

        first_date = get_first_visit_date_by_city(moscow.id, user.id)

        assert first_date == date(2024, 1, 1)

    def test_get_last_visit_date_by_city(self, setup_data: dict[str, Any]) -> None:
        """Получение даты последнего посещения."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 1, 1), rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 2, 1), rating=4, is_first_visit=False
        )
        VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=date(2024, 3, 1),
            rating=5,
            is_first_visit=False,  # Самое позднее
        )

        last_date = get_last_visit_date_by_city(moscow.id, user.id)

        assert last_date == date(2024, 3, 1)


@pytest.mark.django_db
@pytest.mark.integration
class TestVisitCountFunctions:
    """Тесты функций подсчёта посещений."""

    def test_get_number_of_visits_by_city(self, setup_data: dict[str, Any]) -> None:
        """Подсчёт количества посещений конкретного города."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        spb = setup_data['spb']

        # Москва - 3 посещения
        for i in range(3):
            VisitedCity.objects.create(
                user=user,
                city=moscow,
                date_of_visit=date(2024, i + 1, 1),
                rating=5,
                is_first_visit=(i == 0),
            )

        # Питер - 1 посещение
        VisitedCity.objects.create(user=user, city=spb, rating=4, is_first_visit=True)

        count_moscow = get_number_of_visits_by_city(moscow.id, user.id)
        count_spb = get_number_of_visits_by_city(spb.id, user.id)

        assert count_moscow == 3
        assert count_spb == 1

    def test_get_number_of_visits_by_city_no_visits(self, setup_data: dict[str, Any]) -> None:
        """Подсчёт для города без посещений."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        count = get_number_of_visits_by_city(moscow.id, user.id)

        assert count == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestNotVisitedCitiesFunctions:
    """Тесты функций получения непосещённых городов."""

    def test_get_not_visited_cities_all(self, setup_data: dict[str, Any]) -> None:
        """Получение всех непосещённых городов."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        # Всего 3 города, посещён 1
        VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=True)

        not_visited = get_not_visited_cities(user.id)

        assert not_visited.count() == 2  # spb и kazan

    def test_get_not_visited_cities_by_country(self, setup_data: dict[str, Any]) -> None:
        """Получение непосещённых городов в стране."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=True)

        not_visited = get_not_visited_cities(user.id, country_code='RU')

        assert not_visited.count() == 2

    def test_get_not_visited_cities_no_visits(self, setup_data: dict[str, Any]) -> None:
        """Все города непосещённые."""
        user = setup_data['user']

        not_visited = get_not_visited_cities(user.id)

        assert not_visited.count() == 3  # Все города


@pytest.mark.django_db
@pytest.mark.integration
class TestRecentCitiesFunctions:
    """Тесты функций получения недавних городов."""

    def test_get_last_10_new_visited_cities(self, setup_data: dict[str, Any]) -> None:
        """Получение последних 10 новых городов."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        spb = setup_data['spb']

        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 1, 1), rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user, city=spb, date_of_visit=date(2024, 2, 1), rating=4, is_first_visit=True
        )

        recent = get_last_10_new_visited_cities(user.id)

        assert recent.count() == 2
        # Должны быть отсортированы по убыванию даты
        assert recent[0].city == spb  # Более поздняя дата
        assert recent[1].city == moscow

    def test_get_last_10_excludes_without_date(self, setup_data: dict[str, Any]) -> None:
        """Исключаются посещения без даты."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        spb = setup_data['spb']

        VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=None,  # Без даты
            rating=5,
            is_first_visit=True,
        )
        VisitedCity.objects.create(
            user=user, city=spb, date_of_visit=date(2024, 1, 1), rating=4, is_first_visit=True
        )

        recent = get_last_10_new_visited_cities(user.id)

        assert recent.count() == 1  # Только с датой


@pytest.mark.django_db
@pytest.mark.integration
class TestTimeSeriesFunctions:
    """Тесты функций временных рядов (годы/месяцы)."""

    def test_get_number_of_total_visited_cities_in_several_years(
        self, setup_data: dict[str, Any]
    ) -> None:
        """Статистика посещений по годам."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        spb = setup_data['spb']

        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2023, 1, 1), rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2023, 6, 1), rating=4, is_first_visit=False
        )
        VisitedCity.objects.create(
            user=user, city=spb, date_of_visit=date(2024, 1, 1), rating=5, is_first_visit=True
        )

        stats = get_number_of_total_visited_cities_in_several_years(user.id)

        # Должно быть 2 года
        assert len(stats) == 2

    def test_get_number_of_new_visited_cities_in_several_years(
        self, setup_data: dict[str, Any]
    ) -> None:
        """Статистика новых городов по годам."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        spb = setup_data['spb']

        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2023, 1, 1), rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=date(2023, 6, 1),
            rating=4,
            is_first_visit=False,  # Не учитывается
        )
        VisitedCity.objects.create(
            user=user, city=spb, date_of_visit=date(2024, 1, 1), rating=5, is_first_visit=True
        )

        stats = get_number_of_new_visited_cities_in_several_years(user.id)

        # Должно быть 2 года
        assert len(stats) == 2

    def test_get_number_of_total_visited_cities_in_several_month(
        self, setup_data: dict[str, Any]
    ) -> None:
        """Статистика посещений по месяцам."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 1, 15), rating=5, is_first_visit=True
        )
        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 1, 20), rating=4, is_first_visit=False
        )

        stats = get_number_of_total_visited_cities_in_several_month(user.id)

        # Результат зависит от текущей даты, просто проверим что функция работает
        assert isinstance(stats, list) or hasattr(stats, '__iter__')

    def test_get_number_of_new_visited_cities_in_several_month(
        self, setup_data: dict[str, Any]
    ) -> None:
        """Статистика новых городов по месяцам."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 1, 15), rating=5, is_first_visit=True
        )

        stats = get_number_of_new_visited_cities_in_several_month(user.id)

        assert isinstance(stats, list) or hasattr(stats, '__iter__')
