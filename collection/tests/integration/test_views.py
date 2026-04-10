"""
Интеграционные тесты для views приложения collection.
"""

from typing import Any
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from city.models import City, CityUserPhoto, VisitedCity
from collection.models import Collection
from collection.views import get_url_params
from country.models import Country
from premium.models import PremiumPlan, PremiumSubscription
from region.models import Region


@pytest.mark.django_db
@pytest.mark.integration
class TestCollectionListView:
    """Тесты для представления CollectionList."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def user(self) -> User:
        """Создает тестового пользователя."""
        return User.objects.create_user(username='testuser', password='testpass')

    @pytest.fixture
    def setup_data(self, user: User, region_type: Any) -> dict[str, Any]:
        """Создает данные для тестов."""
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

        collection1 = Collection.objects.create(title='Столицы')
        collection1.city.add(city1)

        collection2 = Collection.objects.create(title='Города-миллионники')
        collection2.city.add(city1)

        # Посещаем один город
        VisitedCity.objects.create(user=user, city=city1, rating=3, is_first_visit=True)

        return {
            'user': user,
            'collection1': collection1,
            'collection2': collection2,
            'city1': city1,
        }

    def test_view_accessible_for_anonymous(self, client: Client) -> None:
        """Проверяет что представление доступно для анонимных пользователей."""
        response = client.get(reverse('collection-list'))

        assert response.status_code == 200

    def test_view_accessible_for_authenticated(self, client: Client, user: User) -> None:
        """Проверяет что представление доступно для авторизованных пользователей."""
        client.force_login(user)
        response = client.get(reverse('collection-list'))

        assert response.status_code == 200

    def test_view_uses_correct_template(self, client: Client) -> None:
        """Проверяет что используется правильный шаблон."""
        response = client.get(reverse('collection-list'))

        assert 'collection/list/page.html' in [t.name for t in response.templates]

    def test_context_contains_collections(self, client: Client, setup_data: dict[str, Any]) -> None:
        """Проверяет что контекст содержит коллекции."""
        response = client.get(reverse('collection-list'))

        assert 'object_list' in response.context
        assert response.context['object_list'].count() == 2

    def test_context_for_authenticated_user(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет контекст для авторизованного пользователя."""
        user = setup_data['user']
        client.force_login(user)

        response = client.get(reverse('collection-list'))

        assert 'visited_cities' in response.context
        assert 'qty_of_collections' in response.context
        assert 'qty_of_started_colelctions' in response.context
        assert 'qty_of_finished_colelctions' in response.context

    def test_pagination(self, client: Client) -> None:
        """Проверяет пагинацию."""
        # Создаем 20 коллекций
        for i in range(20):
            Collection.objects.create(title=f'Коллекция {i}')

        response = client.get(reverse('collection-list'))

        assert response.context['is_paginated'] is True
        assert len(response.context['object_list']) == 16


@pytest.mark.django_db
@pytest.mark.integration
class TestCollectionSelectedListView:
    """Тесты для представления CollectionSelected_List."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def user(self) -> User:
        """Создает тестового пользователя."""
        return User.objects.create_user(username='testuser', password='testpass')

    @pytest.fixture
    def setup_data(self, user: User, region_type: Any) -> dict[str, Any]:
        """Создает данные для тестов."""
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

        collection = Collection.objects.create(title='Столицы')
        collection.city.set([city1, city2])

        VisitedCity.objects.create(user=user, city=city1, rating=3, is_first_visit=True)

        return {
            'user': user,
            'collection': collection,
            'city1': city1,
            'city2': city2,
        }

    def test_view_accessible_for_anonymous(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет что представление доступно для анонимных пользователей."""
        collection = setup_data['collection']
        response = client.get(reverse('collection-detail-list', kwargs={'pk': collection.pk}))

        assert response.status_code == 200

    def test_view_returns_404_for_non_existent_collection(self, client: Client) -> None:
        """Проверяет что несуществующая коллекция возвращает 404."""
        response = client.get(reverse('collection-detail-list', kwargs={'pk': 99999}))

        assert response.status_code == 404

    def test_context_contains_cities(self, client: Client, setup_data: dict[str, Any]) -> None:
        """Проверяет что контекст содержит города."""
        collection = setup_data['collection']
        response = client.get(reverse('collection-detail-list', kwargs={'pk': collection.pk}))

        assert 'object_list' in response.context
        assert 'qty_of_cities' in response.context
        assert response.context['qty_of_cities'] == 2

    def test_filter_visited_for_authenticated_user(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет фильтрацию посещенных городов для авторизованного пользователя."""
        user = setup_data['user']
        collection = setup_data['collection']
        client.force_login(user)

        response = client.get(
            reverse('collection-detail-list', kwargs={'pk': collection.pk}),
            {'filter': 'visited'},
        )

        assert response.status_code == 200
        assert response.context['filter'] == 'visited'
        # Должен остаться 1 посещенный город
        assert response.context['qty_of_visited_cities'] == 1

    def test_filter_not_visited_for_authenticated_user(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет фильтрацию непосещенных городов для авторизованного пользователя."""
        user = setup_data['user']
        collection = setup_data['collection']
        client.force_login(user)

        response = client.get(
            reverse('collection-detail-list', kwargs={'pk': collection.pk}),
            {'filter': 'not_visited'},
        )

        assert response.status_code == 200
        assert response.context['filter'] == 'not_visited'

    def test_map_template_used_for_map_view(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет что используется шаблон карты."""
        collection = setup_data['collection']
        response = client.get(reverse('collection-detail-map', kwargs={'pk': collection.pk}))

        assert response.status_code == 200
        assert 'collection/selected/map/page.html' in [t.name for t in response.templates]

    @pytest.fixture(autouse=True)
    def use_local_storage_for_city_photos(self, tmp_path: Any) -> Any:
        storage = FileSystemStorage(location=tmp_path, base_url='/media/')
        image_field = CityUserPhoto._meta.get_field('image')
        original_storage = image_field.storage
        image_field.storage = storage
        try:
            yield storage
        finally:
            image_field.storage = original_storage

    def test_collection_list_prefers_user_uploaded_city_photo(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        user = setup_data['user']
        collection = setup_data['collection']
        city2 = setup_data['city2']
        plan = PremiumPlan.objects.create(
            slug='advanced',
            name='Advanced',
            description='Advanced plan',
            price_month=Decimal('599.00'),
            price_year=Decimal('5990.00'),
            currency='RUB',
            is_active=True,
            sort_order=0,
        )
        now = timezone.now()
        PremiumSubscription.objects.create(
            user=user,
            plan=plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.ACTIVE,
            started_at=now,
            expires_at=now + timedelta(days=30),
            provider_payment_id='test-payment',
        )
        photo = CityUserPhoto.objects.create(
            user=user,
            city=city2,
            image=SimpleUploadedFile('city2.jpg', b'fake-image', content_type='image/jpeg'),
            is_default=True,
            position=1,
        )

        client.force_login(user)
        response = client.get(reverse('collection-detail-list', kwargs={'pk': collection.pk}))

        assert response.status_code == 200
        object_list = list(response.context['object_list'])
        city_row = next(item for item in object_list if item.id == city2.id)
        assert str(city_row.default_city_user_photo_id) == str(photo.id)
        assert getattr(city_row, 'default_city_user_photo_url', '').endswith('.jpg')


@pytest.mark.unit
class TestGetUrlParams:
    """Тесты для функции get_url_params."""

    def test_returns_filter_param_for_visited(self) -> None:
        """Проверяет возврат параметра для фильтра visited."""
        result = get_url_params('visited')
        assert result == 'filter=visited'

    def test_returns_filter_param_for_not_visited(self) -> None:
        """Проверяет возврат параметра для фильтра not_visited."""
        result = get_url_params('not_visited')
        assert result == 'filter=not_visited'

    def test_returns_empty_string_for_empty_filter(self) -> None:
        """Проверяет возврат пустой строки для пустого фильтра."""
        result = get_url_params('')
        assert result == ''

    def test_returns_empty_string_for_none(self) -> None:
        """Проверяет возврат пустой строки для None."""
        result = get_url_params(None)
        assert result == ''

    def test_returns_empty_string_for_invalid_filter(self) -> None:
        """Проверяет возврат пустой строки для невалидного фильтра."""
        result = get_url_params('invalid')
        assert result == ''
