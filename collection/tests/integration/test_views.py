# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""
Интеграционные тесты для views приложения collection.
"""

import time
import logging
from typing import Any
from datetime import date, timedelta
from decimal import Decimal

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from city.models import City, CityUserPhoto, VisitedCity
from collection.models import Collection, PersonalCollection
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

    def test_city_filter_returns_only_related_common_collections(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Фильтр города ограничивает каталог связанными общими коллекциями."""
        city = setup_data['city1']
        unrelated = Collection.objects.create(title='Несвязанная общая коллекция')
        personal = PersonalCollection.objects.create(
            title='Персональная коллекция',
            user=setup_data['user'],
        )
        personal.city.add(city)

        response = client.get(reverse('collection-list'), {'city': city.id})

        assert response.status_code == 200
        assert {collection.id for collection in response.context['object_list']} == {
            setup_data['collection1'].id,
            setup_data['collection2'].id,
        }
        assert unrelated.title not in response.content.decode()
        assert personal.title not in response.content.decode()
        assert response.context['selected_city'] == city

    def test_city_filter_badge_resets_city_and_page_but_keeps_other_parameters(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Ссылка бейджа снимает только контекст города и пагинации."""
        city = setup_data['city1']
        city.title = '<Москва>'
        city.save(update_fields=['title'])
        client.force_login(setup_data['user'])

        response = client.get(
            reverse('collection-list'),
            {
                'city': city.id,
                'page': 1,
                'sort': 'name_up',
                'filter': 'finished',
                'source': 'toast',
            },
        )

        content = response.content.decode()
        document = BeautifulSoup(content, 'html.parser')
        reset_link = document.select_one('[aria-label="Сбросить фильтр по городу"]')
        assert response.status_code == 200
        assert 'Город: <Москва>' in document.get_text(' ', strip=True)
        assert 'Город: <Москва>' not in content
        assert reset_link is not None
        assert reset_link['href'] == '/collection/?sort=name_up&filter=finished&source=toast'
        assert {collection.id for collection in response.context['object_list']} == {
            setup_data['collection1'].id,
            setup_data['collection2'].id,
        }

    def test_city_without_common_collections_has_filtered_empty_state(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Пустой результат объясняет отсутствие общих коллекций у выбранного города."""
        city = City.objects.create(
            title='Тула',
            region=setup_data['city1'].region,
            country=setup_data['city1'].country,
            coordinate_width=54.193,
            coordinate_longitude=37.617,
        )

        response = client.get(reverse('collection-list'), {'city': city.id})

        document = BeautifulSoup(response.content, 'html.parser')
        reset_link = document.select_one('[aria-label="Сбросить фильтр по городу"]')
        assert response.status_code == 200
        assert not response.context['object_list']
        assert response.context['selected_city'] == city
        assert 'Город «Тула» не входит ни в одну общую коллекцию' in document.get_text(
            ' ', strip=True
        )
        assert reset_link is not None
        assert reset_link['href'] == '/collection/'

    def test_other_filter_does_not_claim_city_has_no_common_collections(
        self, client: Client, setup_data: dict[str, Any], region_type: Any
    ) -> None:
        """Пустой progress-фильтр не подменяет факт связи города с коллекциями."""
        city = setup_data['city1']
        country = Country.objects.create(name='Беларусь', code='BY')
        region = Region.objects.create(
            title='Минская',
            country=country,
            type=region_type,
            iso3166='BY-MI',
            full_name='Минская область',
        )
        unvisited_city = City.objects.create(
            title='Минск',
            region=region,
            country=country,
            coordinate_width=53.9,
            coordinate_longitude=27.5667,
        )
        for collection in (setup_data['collection1'], setup_data['collection2']):
            collection.city.add(unvisited_city)
        client.force_login(setup_data['user'])

        response = client.get(
            reverse('collection-list'),
            {'city': city.id, 'filter': 'finished'},
        )

        content = BeautifulSoup(response.content, 'html.parser').get_text(' ', strip=True)
        assert response.status_code == 200
        assert not response.context['object_list']
        assert response.context['selected_city_has_common_collections'] is True
        assert 'Город «Москва» не входит ни в одну общую коллекцию' not in content
        assert 'Нет общих коллекций, соответствующих выбранным фильтрам.' in content

    @pytest.mark.parametrize('city_value', ['', 'not-a-number', '-1', '999999'])
    def test_invalid_city_filter_returns_not_found(self, client: Client, city_value: str) -> None:
        """Некорректный или неизвестный идентификатор города не игнорируется."""
        response = client.get(reverse('collection-list'), {'city': city_value})

        assert response.status_code == 404

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

    def test_authenticated_user_sees_collection_timeline_with_unvisited_cities(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Хронология коллекции показывает непосещённые города и все посещения городов коллекции."""
        user = setup_data['user']
        collection = setup_data['collection']
        visited_city = setup_data['city1']
        unvisited_city = setup_data['city2']
        country = visited_city.country
        undated_city = City.objects.create(
            title='Город без даты',
            region=visited_city.region,
            country=country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )
        older_visited_city = City.objects.create(
            title='Старый посещённый город',
            region=visited_city.region,
            country=country,
            coordinate_width=56.5,
            coordinate_longitude=38.5,
        )
        collection.city.add(undated_city)
        collection.city.add(older_visited_city)

        VisitedCity.objects.filter(user=user, city=visited_city).delete()
        VisitedCity.objects.create(
            user=user, city=visited_city, date_of_visit=date(2024, 5, 2), rating=5
        )
        VisitedCity.objects.create(
            user=user, city=visited_city, date_of_visit=date(2024, 1, 1), rating=4
        )
        VisitedCity.objects.create(
            user=user, city=older_visited_city, date_of_visit=date(2023, 6, 3), rating=4
        )
        VisitedCity.objects.create(user=user, city=undated_city, date_of_visit=None, rating=3)

        client.force_login(user)
        response = client.get(reverse('collection-detail-list', kwargs={'pk': collection.pk}))

        assert response.status_code == 200
        timeline_items = response.context['collection_timeline_items']
        assert [item['city_title'] for item in timeline_items] == [
            unvisited_city.title,
            visited_city.title,
            visited_city.title,
            older_visited_city.title,
            undated_city.title,
        ]
        assert [item['date_label'] for item in timeline_items] == [
            'Не посещён',
            '02.05.2024',
            '01.01.2024',
            '03.06.2023',
            'Без даты',
        ]
        assert [item['status'] for item in timeline_items] == [
            'unvisited',
            'visited',
            'visited',
            'visited',
            'visited',
        ]
        assert [item.get('year') for item in timeline_items] == [None, 2024, 2024, 2023, None]
        assert response.context['collection_timeline_years'] == [2024, 2023]

        content = response.content.decode()
        assert 'id="collection-timeline-modal"' in content
        assert 'dui-modal' in content
        assert 'dui-timeline dui-timeline-vertical' in content
        assert 'data-timeline-modal-trigger="collection-timeline-modal"' in content
        assert 'data-timeline-scroll-container' in content
        assert content.count('data-timeline-first-visited') == 1
        assert 'data-timeline-year="2024"' in content
        assert 'data-timeline-year="2023"' in content
        assert 'dui-collapse' in content
        assert 'dui-filter' in content
        assert 'data-timeline-year-filter="2024"' in content
        assert 'data-timeline-year-filter="2023"' in content
        assert 'Хронология' in content

    def test_map_template_used_for_map_view(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет что используется шаблон карты."""
        collection = setup_data['collection']
        response = client.get(reverse('collection-detail-map', kwargs={'pk': collection.pk}))

        assert response.status_code == 200
        assert 'collection/selected/map/page.html' in [t.name for t in response.templates]

    def test_map_view_does_not_build_timeline_items(
        self, client: Client, setup_data: dict[str, Any]
    ) -> None:
        """Проверяет, что для map-view не собирается collection_timeline_items."""
        user = setup_data['user']
        collection = setup_data['collection']
        client.force_login(user)
        response = client.get(reverse('collection-detail-map', kwargs={'pk': collection.pk}))

        assert response.status_code == 200
        assert 'collection_timeline_items' not in response.context

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
