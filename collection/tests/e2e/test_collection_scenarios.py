"""
E2E тесты для полных сценариев работы с коллекциями.
"""

from typing import Any

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from collection.models import Collection
from country.models import Country
from region.models import Region


@pytest.mark.django_db
@pytest.mark.e2e
class TestCollectionFullWorkflow:
    """Сквозные тесты для полного сценария работы с коллекциями."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def user(self) -> User:
        """Создает тестового пользователя."""
        return User.objects.create_user(
            username='testuser', password='testpass', email='test@test.com'
        )

    @pytest.fixture
    def setup_collections(self, user: User, region_type: Any) -> dict[str, Any]:
        """Создает полноценную структуру коллекций и городов."""
        country = Country.objects.create(name='Россия', code='RU')
        region1 = Region.objects.create(
            title='Москва',
            country=country,
            type=region_type,
            iso3166='RU-MOW-E2E',
            full_name='г. Москва',
        )
        region2 = Region.objects.create(
            title='Санкт-Петербург',
            country=country,
            type=region_type,
            iso3166='RU-SPE-E2E',
            full_name='г. Санкт-Петербург',
        )

        # Создаем города
        moscow = City.objects.create(
            title='Москва',
            region=region1,
            country=country,
            coordinate_width='55.7558',
            coordinate_longitude='37.6173',
            population=12000000,
        )
        spb = City.objects.create(
            title='Санкт-Петербург',
            region=region2,
            country=country,
            coordinate_width='59.9343',
            coordinate_longitude='30.3351',
            population=5000000,
        )
        kazan = City.objects.create(
            title='Казань',
            region=region1,
            country=country,
            coordinate_width='55.8304',
            coordinate_longitude='49.0661',
            population=1200000,
        )
        ekb = City.objects.create(
            title='Екатеринбург',
            region=region1,
            country=country,
            coordinate_width='56.8389',
            coordinate_longitude='60.6057',
            population=1500000,
        )

        # Создаем коллекции
        capitals = Collection.objects.create(title='Столицы регионов')
        capitals.city.set([moscow, spb])

        millioners = Collection.objects.create(title='Города-миллионники')
        millioners.city.set([moscow, spb, kazan, ekb])

        golden_ring = Collection.objects.create(title='Золотое кольцо')
        # Пустая коллекция

        return {
            'user': user,
            'moscow': moscow,
            'spb': spb,
            'kazan': kazan,
            'ekb': ekb,
            'capitals': capitals,
            'millioners': millioners,
            'golden_ring': golden_ring,
        }

    def test_anonymous_user_can_view_collection_list(
        self, client: Client, setup_collections: dict[str, Any]
    ) -> None:
        """Анонимный пользователь может просматривать список коллекций."""
        response = client.get(reverse('collection-list'))

        assert response.status_code == 200
        assert 'object_list' in response.context
        assert response.context['qty_of_collections'] == 3

    def test_anonymous_user_can_view_collection_details(
        self, client: Client, setup_collections: dict[str, Any]
    ) -> None:
        """Анонимный пользователь может просматривать детали коллекции."""
        capitals = setup_collections['capitals']

        response = client.get(reverse('collection-detail-list', kwargs={'pk': capitals.pk}))

        assert response.status_code == 200
        assert response.context['qty_of_cities'] == 2
        assert 'cities' in response.context

    def test_user_journey_visiting_cities_in_collection(
        self, client: Client, setup_collections: dict[str, Any]
    ) -> None:
        """Сценарий: пользователь посещает города из коллекции."""
        user = setup_collections['user']
        moscow = setup_collections['moscow']
        spb = setup_collections['spb']
        capitals = setup_collections['capitals']

        client.force_login(user)

        # 1. Просмотр коллекций - нет посещенных
        response = client.get(reverse('collection-list'))
        assert response.status_code == 200
        assert response.context['qty_of_started_colelctions'] == 0

        # 2. Посещаем Москву
        VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=True)

        # 3. Проверяем что коллекция стала "начатой"
        response = client.get(reverse('collection-list'))
        assert response.context['qty_of_started_colelctions'] >= 1

        # 4. Посещаем Санкт-Петербург
        VisitedCity.objects.create(user=user, city=spb, rating=4, is_first_visit=True)

        # 5. Проверяем что коллекция "Столицы" завершена
        response = client.get(reverse('collection-list'))
        assert response.context['qty_of_finished_colelctions'] >= 1

        # 6. Проверяем детали коллекции с фильтром
        response = client.get(
            reverse('collection-detail-list', kwargs={'pk': capitals.pk}),
            {'filter': 'visited'},
        )
        assert response.status_code == 200
        assert response.context['qty_of_visited_cities'] == 2

    def test_user_can_filter_visited_cities_in_collection(
        self, client: Client, setup_collections: dict[str, Any]
    ) -> None:
        """Пользователь может фильтровать посещенные города в коллекции."""
        user = setup_collections['user']
        moscow = setup_collections['moscow']
        millioners = setup_collections['millioners']

        client.force_login(user)

        # Посещаем один город
        VisitedCity.objects.create(user=user, city=moscow, rating=3, is_first_visit=True)

        # Фильтр "посещенные"
        response = client.get(
            reverse('collection-detail-list', kwargs={'pk': millioners.pk}),
            {'filter': 'visited'},
        )
        assert response.status_code == 200

        # Фильтр "непосещенные"
        response = client.get(
            reverse('collection-detail-list', kwargs={'pk': millioners.pk}),
            {'filter': 'not_visited'},
        )
        assert response.status_code == 200

    def test_user_can_view_collection_on_map(
        self, client: Client, setup_collections: dict[str, Any]
    ) -> None:
        """Пользователь может просматривать коллекцию на карте."""
        user = setup_collections['user']
        capitals = setup_collections['capitals']

        client.force_login(user)

        response = client.get(reverse('collection-detail-map', kwargs={'pk': capitals.pk}))

        assert response.status_code == 200
        assert 'all_cities' in response.context
        assert 'collection/selected/map/page.html' in [t.name for t in response.templates]

    def test_search_collections_api_integration(
        self, client: Client, setup_collections: dict[str, Any]
    ) -> None:
        """Поиск коллекций через API."""
        response = client.get('/api/collection/search', {'query': 'Золотое'})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == 'Золотое кольцо'

    def test_empty_collection_displays_correctly(
        self, client: Client, setup_collections: dict[str, Any]
    ) -> None:
        """Пустая коллекция отображается корректно."""
        golden_ring = setup_collections['golden_ring']

        response = client.get(reverse('collection-detail-list', kwargs={'pk': golden_ring.pk}))

        assert response.status_code == 200
        assert response.context['qty_of_cities'] == 0

    def test_collection_progress_tracking(
        self, client: Client, setup_collections: dict[str, Any]
    ) -> None:
        """Отслеживание прогресса по коллекциям."""
        user = setup_collections['user']
        moscow = setup_collections['moscow']
        spb = setup_collections['spb']
        kazan = setup_collections['kazan']

        client.force_login(user)

        # Посещаем 3 из 4 городов коллекции "миллионники"
        VisitedCity.objects.create(user=user, city=moscow, rating=3, is_first_visit=True)
        VisitedCity.objects.create(user=user, city=spb, rating=3, is_first_visit=True)
        VisitedCity.objects.create(user=user, city=kazan, rating=3, is_first_visit=True)

        response = client.get(reverse('collection-list'))

        # Коллекция "миллионники" начата, но не завершена
        assert response.context['qty_of_started_colelctions'] >= 1
        # "Столицы" завершена полностью
        assert response.context['qty_of_finished_colelctions'] >= 1

    def test_multiple_visits_to_same_city_in_collection(
        self, client: Client, setup_collections: dict[str, Any]
    ) -> None:
        """Множественные посещения одного города в коллекции."""
        user = setup_collections['user']
        moscow = setup_collections['moscow']
        capitals = setup_collections['capitals']

        client.force_login(user)

        # Создаем несколько посещений
        VisitedCity.objects.create(user=user, city=moscow, rating=3, is_first_visit=True)
        VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=False)

        response = client.get(reverse('collection-detail-list', kwargs={'pk': capitals.pk}))

        assert response.status_code == 200
        # Город должен считаться посещенным один раз
        assert response.context['qty_of_visited_cities'] == 1
