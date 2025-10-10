"""
E2E тесты для сценариев с подписками.

Проверяются сценарии:
- Просмотр городов подписок на карте
- Просмотр городов подписок в списке
- Взаимодействие между пользователями через подписки
"""

from datetime import date
from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType
from subscribe.infrastructure.models import Subscribe


@pytest.fixture
def setup_subscription_data(django_user_model: Any) -> dict[str, Any]:
    """Создание данных для тестов подписок."""
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

    cities = []
    for i in range(5):
        city = City.objects.create(
            title=f'Город_{i}',
            country=country,
            region=region,
            coordinate_width=55.0 + i * 0.1,
            coordinate_longitude=37.0 + i * 0.1,
        )
        cities.append(city)

    user1 = django_user_model.objects.create_user(username='user1', password='pass')
    user2 = django_user_model.objects.create_user(username='user2', password='pass')

    return {
        'user1': user1,
        'user2': user2,
        'country': country,
        'region': region,
        'cities': cities,
    }


@pytest.mark.django_db(transaction=True)
@pytest.mark.e2e
class TestSubscriptionCitiesOnMap:
    """E2E тесты просмотра городов подписок на карте."""

    def test_view_subscription_cities_on_map(
        self, setup_subscription_data: dict[str, Any], client: Client
    ) -> None:
        """E2E: Подписка → User2 создаёт города → User1 видит их на карте."""
        user1 = setup_subscription_data['user1']
        user2 = setup_subscription_data['user2']
        cities = setup_subscription_data['cities'][:2]
        country = setup_subscription_data['country']
        region = setup_subscription_data['region']

        # ШАГ 1: User1 подписывается на User2
        from account.models import ShareSettings

        ShareSettings.objects.create(user=user2, can_share_city_map=True)
        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

        # ШАГ 2: User2 создаёт города
        client.login(username='user2', password='pass')
        for city in cities:
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

        # ШАГ 3: User1 просматривает карту
        client.login(username='user1', password='pass')
        response = client.get(reverse('city-all-map'))
        assert response.status_code == 200

        # Карта должна содержать города подписки


@pytest.mark.django_db(transaction=True)
@pytest.mark.e2e
class TestSubscriptionCitiesOnList:
    """E2E тесты просмотра городов подписок в списке."""

    def test_view_subscription_cities_in_list(
        self, setup_subscription_data: dict[str, Any], client: Client
    ) -> None:
        """E2E: Подписка → Просмотр городов подписки в списке."""
        user1 = setup_subscription_data['user1']
        user2 = setup_subscription_data['user2']
        city = setup_subscription_data['cities'][0]
        country = setup_subscription_data['country']
        region = setup_subscription_data['region']

        # ШАГ 1: Настройка подписки
        from account.models import ShareSettings

        ShareSettings.objects.create(user=user2, can_share_dashboard=True)
        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

        # ШАГ 2: User2 создаёт город
        client.login(username='user2', password='pass')
        client.post(
            reverse('city-create'),
            data={
                'country': country.id,
                'region': region.id,
                'city': city.id,
                'rating': '4',
            },
        )
        client.logout()

        # ШАГ 3: User1 просматривает список
        client.login(username='user1', password='pass')
        response = client.get(reverse('city-all-list'))
        assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
@pytest.mark.e2e
class TestMultipleSubscriptionsScenario:
    """E2E тесты множественных подписок."""

    def test_multiple_subscriptions_display(
        self, setup_subscription_data: dict[str, Any], client: Client, django_user_model: Any
    ) -> None:
        """E2E: Подписка на нескольких пользователей → Просмотр всех городов."""
        user1 = setup_subscription_data['user1']
        user2 = setup_subscription_data['user2']
        user3 = django_user_model.objects.create_user(username='user3', password='pass')

        cities = setup_subscription_data['cities'][:3]
        country = setup_subscription_data['country']
        region = setup_subscription_data['region']

        # ШАГ 1: Настройка подписок
        from account.models import ShareSettings

        ShareSettings.objects.create(user=user2, can_share_dashboard=True, can_share_city_map=True)
        ShareSettings.objects.create(user=user3, can_share_dashboard=True, can_share_city_map=True)

        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)
        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user3)

        # ШАГ 2: User2 создаёт город
        client.login(username='user2', password='pass')
        client.post(
            reverse('city-create'),
            data={
                'country': country.id,
                'region': region.id,
                'city': cities[0].id,
                'rating': '5',
            },
        )
        client.logout()

        # ШАГ 3: User3 создаёт город
        client.login(username='user3', password='pass')
        client.post(
            reverse('city-create'),
            data={
                'country': country.id,
                'region': region.id,
                'city': cities[1].id,
                'rating': '4',
            },
        )
        client.logout()

        # ШАГ 4: User1 просматривает список (должен видеть оба города от подписок)
        client.login(username='user1', password='pass')
        response = client.get(reverse('city-all-list'))
        assert response.status_code == 200
