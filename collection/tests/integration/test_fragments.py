# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Интеграционные тесты DMR-фрагментов тематических коллекций."""

from datetime import date

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from collection.models import Collection
from country.models import Country
from region.models import Region, RegionType


def create_collection_city(
    number: int, country: Country, region: Region, collection: Collection
) -> City:
    """Создаёт город с координатами и добавляет его в тематическую коллекцию."""
    city = City.objects.create(
        title=f'Город фрагмента {number:02d}',
        country=country,
        region=region,
        coordinate_width=55.0 + number,
        coordinate_longitude=37.0 + number,
    )
    collection.city.add(city)
    return city


@pytest.mark.django_db
@pytest.mark.integration
class TestCollectionListFragments:
    def test_catalog_fragment_preserves_filter_sort_page_progress_and_previews(
        self, client: Client
    ) -> None:
        """Каталог возвращает обновляемые карточки с прогрессом и превью городов."""
        user = User.objects.create_user(username='fragment-user', password='pass123')
        country = Country.objects.create(name='Фрагментия', code='FG')
        region_type = RegionType.objects.create(title='область')
        region = Region.objects.create(
            title='Фрагментская',
            full_name='Фрагментская область',
            country=country,
            type=region_type,
            iso3166='FG-FR',
        )
        for number in range(17):
            collection = Collection.objects.create(title=f'Коллекция фрагмента {number:02d}')
            city = create_collection_city(number, country, region, collection)
            VisitedCity.objects.create(user=user, city=city, rating=5)
        client.force_login(user)

        response = client.get(
            reverse('collection-list-fragment'),
            data={'filter': 'finished', 'sort': 'progress_down', 'page': 2},
        )

        content = response.content.decode()
        document = BeautifulSoup(content, 'html.parser')
        container = document.select_one('[data-visited-city-refresh]')
        assert response.status_code == 200
        assert container is not None
        assert content.count('data-visited-city-refresh') == 1
        assert container.select_one('#toolbar') is not None
        assert container.select_one('#collection-search-combobox') is not None
        assert container.select_one('#collection-list-results') is not None
        assert 'Посещено 1 из 1' in container.get_text(' ', strip=True)
        assert 'Город фрагмента 16' in container.get_text()
        assert container.select_one('[aria-label="Пагинация"]') is not None
        assert response.context['filter'] == 'finished'
        assert response.context['sort'] == 'progress_down'
        assert response.context['page_obj'].number == 2
        assert '<html' not in content

    def test_selected_list_fragment_preserves_filter_page_status_progress_and_timeline(
        self, client: Client
    ) -> None:
        """Список коллекции возвращает статусы городов и хронологию на текущей странице."""
        user = User.objects.create_user(username='selected-fragment-user', password='pass123')
        country = Country.objects.create(name='Тестландия', code='TL')
        region_type = RegionType.objects.create(title='край')
        region = Region.objects.create(
            title='Тестовый',
            full_name='Тестовый край',
            country=country,
            type=region_type,
            iso3166='TL-TS',
        )
        collection = Collection.objects.create(title='Список фрагмента')
        for number in range(17):
            city = create_collection_city(number, country, region, collection)
            VisitedCity.objects.create(
                user=user,
                city=city,
                rating=5,
                date_of_visit=date(2024, 1, 1),
            )
        client.force_login(user)

        response = client.get(
            reverse('collection-detail-list-fragment', kwargs={'pk': collection.pk}),
            data={'filter': 'visited', 'page': 2},
        )

        content = response.content.decode()
        document = BeautifulSoup(content, 'html.parser')
        container = document.select_one('[data-visited-city-refresh]')
        assert response.status_code == 200
        assert container is not None
        assert content.count('data-visited-city-refresh') == 1
        assert container.select_one('#toolbar') is not None
        assert container.select_one('#collection-selected-list-results') is not None
        assert container.select_one('.visited') is not None
        assert 'Посещено 17 городов из 17' in container.get_text(' ', strip=True)
        assert container.select_one('[aria-label="Пагинация"]') is not None
        assert container.select_one('#collection-timeline-modal') is not None
        assert container.select_one('[data-timeline-year-filter="2024"]') is not None
        assert response.context['filter'] == 'visited'
        assert response.context['page_obj'].number == 2
        assert '<html' not in content

    def test_full_pages_contain_one_refresh_root(self, client: Client) -> None:
        """Полные страницы оставляют единственный корень для атомарной замены."""
        user = User.objects.create_user(username='full-page-user', password='pass123')
        country = Country.objects.create(name='Полная страница', code='FP')
        region_type = RegionType.objects.create(title='республика')
        region = Region.objects.create(
            title='Полная',
            full_name='Полная республика',
            country=country,
            type=region_type,
            iso3166='FP-FP',
        )
        collection = Collection.objects.create(title='Полная коллекция')
        city = create_collection_city(1, country, region, collection)
        VisitedCity.objects.create(user=user, city=city, rating=5)
        client.force_login(user)

        catalog = client.get(reverse('collection-list'))
        selected = client.get(reverse('collection-detail-list', kwargs={'pk': collection.pk}))

        assert catalog.content.decode().count('data-visited-city-refresh') == 1
        assert selected.content.decode().count('data-visited-city-refresh') == 1

    @pytest.mark.parametrize(
        ('url_name', 'kwargs'),
        [
            ('collection-list-fragment', {}),
            ('collection-detail-list-fragment', {'pk': 1}),
        ],
    )
    def test_guest_gets_forbidden_response(
        self, client: Client, url_name: str, kwargs: dict[str, int]
    ) -> None:
        """DMR-фрагменты не перенаправляют гостя на страницу входа."""
        response = client.get(reverse(url_name, kwargs=kwargs))

        assert response.status_code == 403
