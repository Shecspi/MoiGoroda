"""
Интеграционные тесты для views приложения collection.
"""

import time
import logging
from typing import Any
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from city.models import City, CityUserPhoto, VisitedCity
from collection.models import Collection
from collection.repository import COLLECTION_LIST_PREVIEW_CITIES_LIMIT
from collection.views import get_url_params
from country.models import Country
from premium.models import PremiumPlan, PremiumSubscription
from region.models import Region


def _create_large_collection_list_dataset(region_type: Any, user: User) -> None:
    """Создаёт тяжёлый набор данных для проверки производительности list view."""
    country = Country.objects.create(name='Россия perf', code='RP')
    region = Region.objects.create(
        title='Perf', country=country, type=region_type, iso3166='RU-PER', full_name='Perf'
    )
    cities = City.objects.bulk_create(
        [
            City(
                title=f'PerfCity {index:04d}',
                region=region,
                country=country,
                coordinate_width=55.0,
                coordinate_longitude=37.0,
            )
            for index in range(60)
        ]
    )
    VisitedCity.objects.bulk_create(
        [
            VisitedCity(user=user, city=cities[index], rating=3, is_first_visit=True)
            for index in range(20)
        ]
    )

    for collection_index in range(12):
        collection = Collection.objects.create(title=f'Perf collection {collection_index:02d}')
        collection.city.set(cities)


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

        assert 'qty_of_collections' in response.context
        assert 'qty_of_started_collections' in response.context
        assert 'qty_of_finished_collections' in response.context
        assert 'personal_collections' in response.context
        assert 'visited_cities' not in response.context

    def test_pagination(self, client: Client) -> None:
        """Проверяет пагинацию."""
        # Создаем 20 коллекций
        for i in range(20):
            Collection.objects.create(title=f'Коллекция {i}')

        response = client.get(reverse('collection-list'))

        assert response.context['is_paginated'] is True
        assert len(response.context['object_list']) == 16

    def test_collection_statistics_counters(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет агрегированные счётчики коллекций для авторизованного пользователя."""
        user = setup_data['user']
        client.force_login(user)

        response = client.get(reverse('collection-list'))

        assert response.context['qty_of_collections'] == 2
        assert response.context['qty_of_started_collections'] == 2
        assert response.context['qty_of_finished_collections'] == 2

    def test_preview_cities_limited_to_ten(
        self, client: Client, setup_data: dict[str, Any], region_type: Any
    ) -> None:
        """Проверяет, что в карточке показывается не более 10 городов."""
        user = setup_data['user']
        country = Country.objects.create(name='Россия 2', code='R2')
        region = Region.objects.create(
            title='Тест', country=country, type=region_type, iso3166='RU-TST', full_name='Тест'
        )
        cities = City.objects.bulk_create(
            [
                City(
                    title=f'City {index:02d}',
                    region=region,
                    country=country,
                    coordinate_width=55.0,
                    coordinate_longitude=37.0,
                )
                for index in range(12)
            ]
        )
        large_collection = Collection.objects.create(title='Большая коллекция')
        large_collection.city.set(cities)

        client.force_login(user)
        response = client.get(reverse('collection-list'))

        card_collection = next(
            item for item in response.context['object_list'] if item.pk == large_collection.pk
        )
        assert len(card_collection.preview_cities) == COLLECTION_LIST_PREVIEW_CITIES_LIMIT
        assert (
            response.context['collection_list_preview_cities_limit']
            == COLLECTION_LIST_PREVIEW_CITIES_LIMIT
        )
        assert card_collection.preview_cities[0].title == 'City 00'

    def test_preview_cities_mark_visited_for_authenticated_user(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет is_visited на превью-городах без visited_cities в шаблоне."""
        user = setup_data['user']
        collection = setup_data['collection1']
        client.force_login(user)

        response = client.get(reverse('collection-list'))

        card_collection = next(
            item for item in response.context['object_list'] if item.pk == collection.pk
        )
        assert card_collection.preview_cities[0].is_visited is True

    def test_anonymous_user_context_has_no_visited_cities(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Для гостя visited_cities не передаётся в контекст — используется city.is_visited."""
        response = client.get(reverse('collection-list'))

        assert response.status_code == 200
        assert 'visited_cities' not in response.context

    @pytest.mark.parametrize('filter_value', ['not_started', 'finished'])
    def test_guest_auth_only_filters_do_not_cause_field_error(
        self, client: Client, setup_data: dict[str, Any], filter_value: str
    ) -> None:
        """Фильтры прогресса недоступны гостю — запрос не падает с FieldError."""
        response = client.get(reverse('collection-list'), {'filter': filter_value})

        assert response.status_code == 200
        assert response.context['filter'] == ''
        assert response.context['object_list'].count() == 2

    @pytest.mark.parametrize('sort_value', ['progress_down', 'progress_up', 'default_auth'])
    def test_guest_auth_only_sorts_do_not_cause_field_error(
        self, client: Client, setup_data: dict[str, Any], sort_value: str
    ) -> None:
        """Сортировки по прогрессу недоступны гостю — запрос не падает с FieldError."""
        response = client.get(reverse('collection-list'), {'sort': sort_value})

        assert response.status_code == 200
        assert response.context['sort'] == 'default_guest'
        assert response.context['object_list'].count() == 2

    def test_guest_can_use_name_sort(self, client: Client, setup_data: dict[str, Any]) -> None:
        """Гость может сортировать по названию."""
        response = client.get(reverse('collection-list'), {'sort': 'name_down'})

        assert response.status_code == 200
        assert response.context['sort'] == 'name_down'

    def test_invalid_sort_logs_warning_not_default_sort_info(
        self, client: Client, setup_data: dict[str, Any], caplog: pytest.LogCaptureFixture
    ) -> None:
        """При ?sort=invalid не логируется info с default_auth — только warning."""
        caplog.set_level(logging.INFO)
        user = setup_data['user']
        client.force_login(user)

        response = client.get(reverse('collection-list'), {'sort': 'invalid'})

        assert response.status_code == 200
        assert response.context['sort'] == 'default_auth'
        assert not any('Using the sort' in record.message for record in caplog.records)
        assert any(
            "Unexpected value of the sort 'invalid'" in record.message for record in caplog.records
        )

    def test_valid_sort_logs_applied_sort(
        self, client: Client, setup_data: dict[str, Any], caplog: pytest.LogCaptureFixture
    ) -> None:
        """При валидном sort логируется фактически применённое значение."""
        caplog.set_level(logging.INFO)
        user = setup_data['user']
        client.force_login(user)

        response = client.get(reverse('collection-list'), {'sort': 'name_down'})

        assert response.status_code == 200
        assert response.context['sort'] == 'name_down'
        assert any("Using the sort 'name_down'" in record.message for record in caplog.records)

    @pytest.mark.slow
    def test_collection_list_query_count_and_timing(
        self, client: Client, user: User, region_type: Any, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """
        Проверяет, что list view не делает лишних SQL при большом числе городов.

        До оптимизации здесь были count(), полный проход по queryset и prefetch всех
        городов всех коллекций (сотни строк на коллекцию). После — фиксированное
        число запросов, не растущее с количеством городов в коллекции.
        """
        from collection.repository import CollectionRepository

        _create_large_collection_list_dataset(region_type, user)
        client.force_login(user)
        repository = CollectionRepository()

        # Имитация старого get_queryset: count + полная итерация + prefetch всех городов
        # + загрузка всех ID посещённых городов пользователя.
        old_queryset = repository.get_collections_with_annotations(user).prefetch_related('city')
        old_started = time.perf_counter()
        with CaptureQueriesContext(connection) as old_queries:
            old_count = old_queryset.count()
            old_started_count = 0
            old_finished_count = 0
            old_cities_loaded = 0
            for collection in old_queryset:
                old_cities_loaded += collection.city.all().count()
                if collection.qty_of_visited_cities > 0:
                    old_started_count += 1
                if collection.qty_of_visited_cities == collection.qty_of_cities:
                    old_finished_count += 1
            old_visited_cities = list(
                VisitedCity.objects.filter(user=user).values_list('city__id', flat=True)
            )
        old_elapsed = time.perf_counter() - old_started

        connection.queries_log.clear()
        started_at = time.perf_counter()
        with CaptureQueriesContext(connection) as new_queries:
            response = client.get(reverse('collection-list'))
        new_elapsed = time.perf_counter() - started_at
        new_cities_loaded = sum(
            len(collection.preview_cities) for collection in response.context['object_list']
        )

        assert response.status_code == 200
        assert len(response.context['object_list']) == 12
        assert old_count == 12
        assert old_cities_loaded == 12 * 60
        assert new_cities_loaded <= 12 * 10
        assert new_cities_loaded < old_cities_loaded
        assert len(new_queries) <= 12, (
            f'Слишком много SQL-запросов: {len(new_queries)}. '
            f'Запросы: {[query["sql"][:120] for query in new_queries]}'
        )
        assert len(old_visited_cities) == 20

        print(
            f'\n[collection-list perf] '
            f'old get_queryset path: queries={len(old_queries)}, time={old_elapsed:.3f}s, '
            f'cities_loaded={old_cities_loaded}, visited_ids={len(old_visited_cities)} | '
            f'new full page: queries={len(new_queries)}, time={new_elapsed:.3f}s, '
            f'cities_loaded={new_cities_loaded} | '
            f'collections=12, cities_per_collection=60, preview_limit=10'
        )


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
