"""
Integration тесты для бизнес-логики DB Services (city/services/db.py).

Тестируется критичная функция:
- set_is_visit_first_for_all_visited_cities (обновление флага is_first_visit)

Это ключевая бизнес-логика, которая определяет какое посещение города
считается первым (по самой ранней дате).
"""

from datetime import date
from typing import Any

import pytest

from city.models import City, VisitedCity
from city.services.db import set_is_visit_first_for_all_visited_cities
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType


@pytest.fixture
def setup_data(django_user_model: Any) -> dict[str, Any]:
    """Создание базовых данных."""
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

    user = django_user_model.objects.create_user(username='testuser', password='pass')

    return {
        'user': user,
        'moscow': moscow,
    }


@pytest.mark.django_db
@pytest.mark.integration
class TestSetIsFirstVisitBusinessLogic:
    """Тесты критичной бизнес-логики set_is_visit_first_for_all_visited_cities."""

    def test_sets_first_visit_for_earliest_date(self, setup_data: dict[str, Any]) -> None:
        """Первым посещением должна стать запись с самой ранней датой."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        # Создаём посещения в произвольном порядке
        visit1 = VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 3, 1), rating=5, is_first_visit=False
        )
        visit2 = VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=date(2024, 1, 1),  # Самая ранняя
            rating=4,
            is_first_visit=False,
        )
        visit3 = VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 2, 1), rating=5, is_first_visit=False
        )

        # Применяем бизнес-логику
        set_is_visit_first_for_all_visited_cities(moscow.id, user)

        # Перезагружаем из БД
        visit1.refresh_from_db()
        visit2.refresh_from_db()
        visit3.refresh_from_db()

        # Проверяем
        assert visit1.is_first_visit is False
        assert visit2.is_first_visit is True  # Самая ранняя дата
        assert visit3.is_first_visit is False

    def test_sets_first_visit_for_null_date_if_no_dates(self, setup_data: dict[str, Any]) -> None:
        """Если нет дат, первым становится посещение без даты."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        visit1 = VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=None, rating=5, is_first_visit=False
        )
        visit2 = VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=None, rating=4, is_first_visit=False
        )

        set_is_visit_first_for_all_visited_cities(moscow.id, user)

        visit1.refresh_from_db()
        visit2.refresh_from_db()

        # Первая запись (по порядку создания) должна стать is_first_visit=True
        assert visit1.is_first_visit is True
        assert visit2.is_first_visit is False

    def test_prefers_null_date_over_dates(self, setup_data: dict[str, Any]) -> None:
        """NULL дата имеет приоритет перед любыми датами (nulls_first)."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        visit_with_date = VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=date(2020, 1, 1),  # Очень старая дата
            rating=5,
            is_first_visit=False,
        )
        visit_without_date = VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=None,  # NULL имеет приоритет
            rating=4,
            is_first_visit=False,
        )

        set_is_visit_first_for_all_visited_cities(moscow.id, user)

        visit_with_date.refresh_from_db()
        visit_without_date.refresh_from_db()

        # NULL дата должна быть первой
        assert visit_without_date.is_first_visit is True
        assert visit_with_date.is_first_visit is False

    def test_resets_previously_set_flags(self, setup_data: dict[str, Any]) -> None:
        """Сбрасывает предыдущие флаги is_first_visit."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        # Создаём с неправильными флагами
        visit1 = VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=date(2024, 2, 1),
            rating=5,
            is_first_visit=True,  # Неправильно
        )
        visit2 = VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=date(2024, 1, 1),  # Должна быть первой
            rating=4,
            is_first_visit=False,
        )

        # Исправляем
        set_is_visit_first_for_all_visited_cities(moscow.id, user)

        visit1.refresh_from_db()
        visit2.refresh_from_db()

        # Проверяем что флаги обновились правильно
        assert visit1.is_first_visit is False
        assert visit2.is_first_visit is True

    def test_handles_single_visit(self, setup_data: dict[str, Any]) -> None:
        """Обработка единственного посещения."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        visit = VisitedCity.objects.create(
            user=user, city=moscow, date_of_visit=date(2024, 1, 1), rating=5, is_first_visit=False
        )

        set_is_visit_first_for_all_visited_cities(moscow.id, user)

        visit.refresh_from_db()

        assert visit.is_first_visit is True

    def test_handles_no_visits(self, setup_data: dict[str, Any]) -> None:
        """Обработка случая когда нет посещений."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        # Не должно быть ошибки
        set_is_visit_first_for_all_visited_cities(moscow.id, user)

    def test_only_affects_specific_city_and_user(
        self, setup_data: dict[str, Any], django_user_model: Any
    ) -> None:
        """Функция влияет только на посещения конкретного города и пользователя."""
        user1 = setup_data['user']
        user2 = django_user_model.objects.create_user(username='user2', password='pass')
        moscow = setup_data['moscow']

        # Создаём посещения разных пользователей
        visit_user1 = VisitedCity.objects.create(
            user=user1, city=moscow, date_of_visit=date(2024, 1, 1), rating=5, is_first_visit=False
        )
        visit_user2 = VisitedCity.objects.create(
            user=user2, city=moscow, date_of_visit=date(2024, 1, 1), rating=4, is_first_visit=False
        )

        # Обновляем только для user1
        set_is_visit_first_for_all_visited_cities(moscow.id, user1)

        visit_user1.refresh_from_db()
        visit_user2.refresh_from_db()

        # Только user1 должен быть обновлён
        assert visit_user1.is_first_visit is True
        assert visit_user2.is_first_visit is False

    def test_complex_scenario_with_multiple_changes(self, setup_data: dict[str, Any]) -> None:
        """Сложный сценарий: несколько посещений с разными датами."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        # Создаём 5 посещений в произвольном порядке
        visits = [
            VisitedCity.objects.create(
                user=user,
                city=moscow,
                date_of_visit=date(2024, 5, 1),
                rating=5,
                is_first_visit=True,  # Неправильно
            ),
            VisitedCity.objects.create(
                user=user,
                city=moscow,
                date_of_visit=date(2024, 2, 1),  # Должна быть первой
                rating=4,
                is_first_visit=False,
            ),
            VisitedCity.objects.create(
                user=user,
                city=moscow,
                date_of_visit=date(2024, 4, 1),
                rating=3,
                is_first_visit=False,
            ),
            VisitedCity.objects.create(
                user=user,
                city=moscow,
                date_of_visit=date(2024, 3, 1),
                rating=5,
                is_first_visit=False,
            ),
            VisitedCity.objects.create(
                user=user,
                city=moscow,
                date_of_visit=date(2024, 1, 1),
                rating=4,
                is_first_visit=False,
            ),
        ]

        # Ожидаем что visit с date=2024-01-01 станет первым
        # Но мы создали его последним, и он должен иметь самый большой id
        # Нужно проверить что сортировка работает по дате, а не по id

        # На самом деле с nulls_first самой первой должна быть запись без даты
        # Но у нас все с датами, поэтому первой будет 2024-01-01

        set_is_visit_first_for_all_visited_cities(moscow.id, user)

        for visit in visits:
            visit.refresh_from_db()

        # Проверяем что только запись с самой ранней датой имеет is_first_visit=True
        first_visits = [v for v in visits if v.is_first_visit]
        assert len(first_visits) == 1
        assert first_visits[0].date_of_visit == date(2024, 1, 1)

    def test_preserves_other_fields(self, setup_data: dict[str, Any]) -> None:
        """Функция не меняет другие поля кроме is_first_visit."""
        user = setup_data['user']
        moscow = setup_data['moscow']

        visit = VisitedCity.objects.create(
            user=user,
            city=moscow,
            date_of_visit=date(2024, 1, 1),
            rating=5,
            has_magnet=True,
            impression='Отличный город!',
            is_first_visit=False,
        )

        original_rating = visit.rating
        original_magnet = visit.has_magnet
        original_impression = visit.impression
        original_date = visit.date_of_visit

        set_is_visit_first_for_all_visited_cities(moscow.id, user)

        visit.refresh_from_db()

        # Проверяем что изменился только is_first_visit
        assert visit.is_first_visit is True  # Изменилось
        assert visit.rating == original_rating  # Не изменилось
        assert visit.has_magnet == original_magnet  # Не изменилось
        assert visit.impression == original_impression  # Не изменилось
        assert visit.date_of_visit == original_date  # Не изменилось
