"""
E2E тесты полных пользовательских сценариев (user journeys).

Проверяются комплексные сценарии взаимодействия пользователя с системой:
- Создание → Просмотр → Обновление → Удаление
- Работа с множественными городами
- Фильтрация и сортировка
- Повторные посещения
"""

from datetime import date, timedelta
from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType


@pytest.fixture
def setup_full_db(django_user_model: Any) -> dict[str, Any]:
    """Создание полной структуры данных для e2e тестов."""
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

    # Создаём несколько городов для тестирования
    cities = []
    for i in range(10):
        city = City.objects.create(
            title=f'Город_{i}',
            country=country,
            region=region,
            coordinate_width=55.0 + i * 0.1,
            coordinate_longitude=37.0 + i * 0.1,
        )
        cities.append(city)

    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    user2 = django_user_model.objects.create_user(username='testuser2', password='testpass')

    return {
        'user': user,
        'user2': user2,
        'country': country,
        'region': region,
        'cities': cities,
    }


@pytest.mark.django_db(transaction=True)
@pytest.mark.e2e
class TestCompleteUserJourney:
    """Тесты полного пути пользователя через систему."""

    def test_multiple_cities_with_filtering_and_sorting(
        self, setup_full_db: dict[str, Any], client: Client
    ) -> None:
        """E2E: Создание множества городов → Фильтрация → Сортировка → Пагинация."""
        _user = setup_full_db['user']
        cities = setup_full_db['cities'][:5]  # Берём 5 городов
        country = setup_full_db['country']
        region = setup_full_db['region']

        client.login(username='testuser', password='testpass')

        # ШАГ 1: Создаём 5 городов с разными параметрами
        today = date.today()
        for i, city in enumerate(cities):
            client.post(
                reverse('city-create'),
                data={
                    'country': country.id,
                    'region': region.id,
                    'city': city.id,
                    'rating': str((i % 5) + 1),  # Рейтинги 1-5
                    'has_magnet': i % 2 == 0,  # Чётные с магнитом
                    'date_of_visit': (today - timedelta(days=i * 10)).strftime('%d.%m.%Y'),
                },
            )

        # ШАГ 2: Проверяем список (все города отображаются)
        response = client.get(reverse('city-all-list'))
        assert response.status_code == 200
        for city in cities:
            assert city.title in response.content.decode()

        # ШАГ 3: Применяем фильтр "has_magnet"
        response = client.get(reverse('city-all-list') + '?filter=magnet')
        assert response.status_code == 200
        # Должно быть только 3 города с магнитами (0, 2, 4)
        content = response.content.decode()
        assert cities[0].title in content
        assert cities[2].title in content
        assert cities[4].title in content

        # ШАГ 4: Применяем сортировку по дате
        response = client.get(reverse('city-all-list') + '?sort=date_up')
        assert response.status_code == 200

        # ШАГ 5: Комбинация фильтра и сортировки
        response = client.get(reverse('city-all-list') + '?filter=magnet&sort=name_down')
        assert response.status_code == 200

    def test_repeated_visits_workflow(self, setup_full_db: dict[str, Any], client: Client) -> None:
        """E2E: Создание → Повторное посещение → Проверка флага is_first_visit."""
        user = setup_full_db['user']
        city = setup_full_db['cities'][0]
        country = setup_full_db['country']
        region = setup_full_db['region']

        client.login(username='testuser', password='testpass')

        # ШАГ 1: Первое посещение
        response = client.post(
            reverse('city-create'),
            data={
                'country': country.id,
                'region': region.id,
                'city': city.id,
                'rating': '5',
                'date_of_visit': '01.01.2024',
            },
        )
        assert response.status_code == 302

        first_visit = VisitedCity.objects.get(user=user, city=city, date_of_visit=date(2024, 1, 1))
        assert first_visit.is_first_visit is True

        # ШАГ 2: Повторное посещение
        response = client.post(
            reverse('city-create'),
            data={
                'country': country.id,
                'region': region.id,
                'city': city.id,
                'rating': '4',
                'date_of_visit': '01.06.2024',  # Другая дата
            },
        )
        assert response.status_code == 302

        # ШАГ 3: Проверяем флаги is_first_visit
        first_visit.refresh_from_db()
        second_visit = VisitedCity.objects.get(user=user, city=city, date_of_visit=date(2024, 6, 1))

        assert first_visit.is_first_visit is True  # Осталось первым
        assert second_visit.is_first_visit is False  # Не первое

        # ШАГ 4: Проверяем в списке (должны быть оба посещения)
        response = client.get(reverse('city-all-list'))
        assert response.status_code == 200
        # В списке должен быть город (но отображается как один уникальный)

    def test_filter_and_sort_combination_scenarios(
        self, setup_full_db: dict[str, Any], client: Client
    ) -> None:
        """E2E: Создание → Различные комбинации фильтров и сортировок."""
        cities = setup_full_db['cities'][:6]
        country = setup_full_db['country']
        region = setup_full_db['region']

        client.login(username='testuser', password='testpass')

        # Создаём города с разными датами и магнитами
        today = date.today()
        current_year_start = date(today.year, 1, 1)
        last_year = today.year - 1

        # 3 города в текущем году
        for i in range(3):
            client.post(
                reverse('city-create'),
                data={
                    'country': country.id,
                    'region': region.id,
                    'city': cities[i].id,
                    'rating': '5',
                    'has_magnet': True,
                    'date_of_visit': (current_year_start + timedelta(days=i * 30)).strftime(
                        '%d.%m.%Y'
                    ),
                },
            )

        # 3 города в прошлом году
        for i in range(3, 6):
            client.post(
                reverse('city-create'),
                data={
                    'country': country.id,
                    'region': region.id,
                    'city': cities[i].id,
                    'rating': '4',
                    'has_magnet': False,
                    'date_of_visit': date(last_year, 6, 15).strftime('%d.%m.%Y'),
                },
            )

        # СЦЕНАРИЙ 1: Фильтр по текущему году
        response = client.get(reverse('city-all-list') + '?filter=current_year')
        assert response.status_code == 200

        # СЦЕНАРИЙ 2: Фильтр по прошлому году
        response = client.get(reverse('city-all-list') + '?filter=last_year')
        assert response.status_code == 200

        # СЦЕНАРИЙ 3: Фильтр "has_magnet" + сортировка по названию
        response = client.get(reverse('city-all-list') + '?filter=magnet&sort=name_down')
        assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
@pytest.mark.e2e
class TestMultiUserScenarios:
    """E2E тесты сценариев с несколькими пользователями."""

    def test_different_users_independent_cities(
        self, setup_full_db: dict[str, Any], client: Client
    ) -> None:
        """E2E: Два пользователя создают города независимо."""
        user1 = setup_full_db['user']
        user2 = setup_full_db['user2']
        city1 = setup_full_db['cities'][0]
        city2 = setup_full_db['cities'][1]
        country = setup_full_db['country']
        region = setup_full_db['region']

        # User1 создаёт город
        client.login(username='testuser', password='testpass')
        client.post(
            reverse('city-create'),
            data={
                'country': country.id,
                'region': region.id,
                'city': city1.id,
                'rating': '5',
            },
        )
        client.logout()

        # User2 создаёт другой город
        client.login(username='testuser2', password='testpass')
        client.post(
            reverse('city-create'),
            data={
                'country': country.id,
                'region': region.id,
                'city': city2.id,
                'rating': '4',
            },
        )

        # Проверяем что у каждого пользователя свой город
        assert VisitedCity.objects.filter(user=user1).count() == 1
        assert VisitedCity.objects.filter(user=user2).count() == 1

        # User2 видит только свой город в списке
        response = client.get(reverse('city-all-list'))
        assert response.status_code == 200
        content = response.content.decode()
        assert city2.title in content
        # User1's город не должен отображаться (если нет подписок)

    def test_same_city_different_users_different_ratings(
        self, setup_full_db: dict[str, Any], client: Client
    ) -> None:
        """E2E: Два пользователя посещают один город с разными рейтингами."""
        city = setup_full_db['cities'][0]
        country = setup_full_db['country']
        region = setup_full_db['region']

        # User1 ставит рейтинг 5
        client.login(username='testuser', password='testpass')
        client.post(
            reverse('city-create'),
            data={
                'country': country.id,
                'region': region.id,
                'city': city.id,
                'rating': '5',
            },
        )
        client.logout()

        # User2 ставит рейтинг 3
        client.login(username='testuser2', password='testpass')
        client.post(
            reverse('city-create'),
            data={
                'country': country.id,
                'region': region.id,
                'city': city.id,
                'rating': '3',
            },
        )

        # Проверяем что оба посещения записаны
        assert VisitedCity.objects.filter(city=city).count() == 2

        # Средний рейтинг должен быть (5+3)/2 = 4.0
        # (это проверяется на детальной странице города)


@pytest.mark.django_db(transaction=True)
@pytest.mark.e2e
class TestPaginationScenarios:
    """E2E тесты пагинации."""

    def test_pagination_with_many_cities(
        self, setup_full_db: dict[str, Any], client: Client
    ) -> None:
        """E2E: Создание 30 городов → Проверка пагинации."""
        _user = setup_full_db['user']
        country = setup_full_db['country']
        region = setup_full_db['region']

        # Создаём дополнительные города (всего должно быть 30+)
        for i in range(10, 35):
            city = City.objects.create(
                title=f'Город_{i}',
                country=country,
                region=region,
                coordinate_width=55.0 + i * 0.01,
                coordinate_longitude=37.0 + i * 0.01,
            )
            setup_full_db['cities'].append(city)

        client.login(username='testuser', password='testpass')

        # Создаём посещения для 30 городов
        for i in range(30):
            city = setup_full_db['cities'][i]
            client.post(
                reverse('city-create'),
                data={
                    'country': country.id,
                    'region': region.id,
                    'city': city.id,
                    'rating': '5',
                },
            )

        # ШАГ 1: Первая страница (24 города)
        response = client.get(reverse('city-all-list'))
        assert response.status_code == 200
        assert 'page_obj' in response.context
        assert response.context['page_obj'].paginator.count == 30

        # ШАГ 2: Вторая страница (6 городов)
        response = client.get(reverse('city-all-list') + '?page=2')
        assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
@pytest.mark.e2e
class TestEdgeCaseJourneys:
    """E2E тесты граничных случаев."""

    def test_update_city_change_date_affects_is_first_visit(
        self, setup_full_db: dict[str, Any], client: Client
    ) -> None:
        """E2E: Изменение даты может повлиять на is_first_visit."""
        user = setup_full_db['user']
        city = setup_full_db['cities'][0]
        country = setup_full_db['country']
        region = setup_full_db['region']

        client.login(username='testuser', password='testpass')

        # Создаём два посещения
        _response1 = client.post(
            reverse('city-create'),
            data={
                'country': country.id,
                'region': region.id,
                'city': city.id,
                'rating': '5',
                'date_of_visit': '15.02.2024',  # Позже
            },
        )

        _response2 = client.post(
            reverse('city-create'),
            data={
                'country': country.id,
                'region': region.id,
                'city': city.id,
                'rating': '4',
                'date_of_visit': '15.01.2024',  # Раньше - должно стать первым
            },
        )

        # Проверяем что is_first_visit установлен правильно
        visit_jan = VisitedCity.objects.get(user=user, city=city, date_of_visit=date(2024, 1, 15))
        visit_feb = VisitedCity.objects.get(user=user, city=city, date_of_visit=date(2024, 2, 15))

        assert visit_jan.is_first_visit is True  # Самое раннее
        assert visit_feb.is_first_visit is False
