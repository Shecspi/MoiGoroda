# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Интеграционные тесты DMR-фрагментов персональных коллекций."""

from datetime import date

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from collection.models import PersonalCollection
from country.models import Country
from region.models import Region, RegionType


def create_personal_collection_city(
    number: int, country: Country, region: Region, collection: PersonalCollection
) -> City:
    """Создаёт город и добавляет его в персональную коллекцию."""
    city = City.objects.create(
        title=f'Город персонального фрагмента {number:02d}',
        country=country,
        region=region,
        coordinate_width=55.0 + number,
        coordinate_longitude=37.0 + number,
    )
    collection.city.add(city)
    return city


@pytest.fixture
def personal_fragment_data() -> tuple[User, User, Country, Region]:
    """Создаёт владельца, стороннего читателя и географию для фрагментов."""
    owner = User.objects.create_user(username='personal-owner', password='pass123')
    reader = User.objects.create_user(username='personal-reader', password='pass123')
    country = Country.objects.create(name='Персоналия', code='PC')
    region_type = RegionType.objects.create(title='область')
    region = Region.objects.create(
        title='Персональная',
        full_name='Персональная область',
        country=country,
        type=region_type,
        iso3166='PC-PR',
    )
    return owner, reader, country, region


@pytest.mark.django_db
@pytest.mark.integration
class TestPersonalCollectionFragments:
    def test_catalog_fragment_returns_only_owner_membership_progress_and_pagination(
        self, client: Client, personal_fragment_data: tuple[User, User, Country, Region]
    ) -> None:
        """Каталог владельца сохраняет membership, прогресс и страницу."""
        owner, reader, country, region = personal_fragment_data
        for number in range(17):
            collection = PersonalCollection.objects.create(
                user=owner, title=f'Коллекция {number:02d}'
            )
            city = create_personal_collection_city(number, country, region, collection)
            VisitedCity.objects.create(user=owner, city=city, rating=5)
        foreign_collection = PersonalCollection.objects.create(user=reader, title='Чужая коллекция')
        create_personal_collection_city(99, country, region, foreign_collection)
        client.force_login(owner)

        response = client.get(reverse('collection-personal-list-fragment'), data={'page': 2})

        content = response.content.decode()
        container = BeautifulSoup(content, 'html.parser').select_one('[data-visited-city-refresh]')
        assert response.status_code == 200
        assert container is not None
        assert content.count('data-visited-city-refresh') == 1
        assert container.select_one('[id^="personal-collection-card-"]') is not None
        assert 'Чужая коллекция' not in container.get_text(' ', strip=True)
        assert 'Посещено 1 из 1' in container.get_text(' ', strip=True)
        assert container.select_one('[aria-label="Пагинация"]') is not None
        assert response.context['page_obj'].number == 2
        assert '<html' not in content

    def test_catalog_fragment_returns_empty_state(
        self, client: Client, django_user_model: type[User]
    ) -> None:
        """Пустой каталог владельца остаётся самостоятельным фрагментом."""
        owner = django_user_model.objects.create_user(username='empty-owner', password='pass123')
        client.force_login(owner)

        response = client.get(reverse('collection-personal-list-fragment'))

        container = BeautifulSoup(response.content, 'html.parser').select_one(
            '[data-visited-city-refresh]'
        )
        assert response.status_code == 200
        assert container is not None
        assert 'У вас пока нет персональных коллекций.' in container.get_text(' ', strip=True)

    def test_city_list_fragment_preserves_membership_progress_filter_empty_state_and_page(
        self, client: Client, personal_fragment_data: tuple[User, User, Country, Region]
    ) -> None:
        """Список городов возвращает актуальные filter, progress, empty state и pagination."""
        owner, _, country, region = personal_fragment_data
        collection = PersonalCollection.objects.create(user=owner, title='Маршрут владельца')
        for number in range(17):
            city = create_personal_collection_city(number, country, region, collection)
            VisitedCity.objects.create(
                user=owner, city=city, rating=5, date_of_visit=date(2024, 1, 1)
            )
        client.force_login(owner)
        url = reverse('collection-personal-city-list-fragment', kwargs={'pk': collection.pk})

        response = client.get(url, data={'filter': 'visited', 'page': '2'})

        content = response.content.decode()
        container = BeautifulSoup(content, 'html.parser').select_one('[data-visited-city-refresh]')
        assert response.status_code == 200
        assert container is not None
        assert content.count('data-visited-city-refresh') == 1
        assert container.select_one('#toolbar') is not None
        assert container.select_one('#collection-public-status-switch') is not None
        assert 'Посещено 17 городов из 17' in container.get_text(' ', strip=True)
        assert 'Город персонального фрагмента 16' in container.get_text(' ', strip=True)
        assert container.select_one('[aria-label="Пагинация"]') is not None
        assert response.context['filter'] == 'visited'
        assert response.context['page_obj'].number == 2
        assert '<html' not in content

        empty_response = client.get(url, data={'filter': 'not_visited'})
        empty_container = BeautifulSoup(empty_response.content, 'html.parser').select_one(
            '[data-visited-city-refresh]'
        )
        assert empty_response.status_code == 200
        assert empty_container is not None
        assert 'На данный момент в этой коллекции нет ни одного города' in empty_container.get_text(
            ' ', strip=True
        )

    def test_city_list_fragment_keeps_public_reader_access_and_read_only_controls(
        self, client: Client, personal_fragment_data: tuple[User, User, Country, Region]
    ) -> None:
        """Аутентифицированный читатель публичной коллекции получает read-only fragment."""
        owner, reader, country, region = personal_fragment_data
        collection = PersonalCollection.objects.create(
            user=owner, title='Публичный маршрут', is_public=True
        )
        create_personal_collection_city(1, country, region, collection)
        client.force_login(reader)

        response = client.get(
            reverse('collection-personal-city-list-fragment', kwargs={'pk': collection.pk})
        )

        container = BeautifulSoup(response.content, 'html.parser').select_one(
            '[data-visited-city-refresh]'
        )
        assert response.status_code == 200
        assert container is not None
        assert container.select_one('#collection-public-status-switch') is None
        assert container.select_one('#delete-collection-button') is None

    def test_city_list_fragment_preserves_private_collection_access(
        self, client: Client, personal_fragment_data: tuple[User, User, Country, Region]
    ) -> None:
        """Приватный fragment виден владельцу и скрыт от другого пользователя."""
        owner, reader, country, region = personal_fragment_data
        collection = PersonalCollection.objects.create(user=owner, title='Приватный маршрут')
        create_personal_collection_city(1, country, region, collection)
        url = reverse('collection-personal-city-list-fragment', kwargs={'pk': collection.pk})

        client.force_login(owner)
        assert client.get(url).status_code == 200

        client.force_login(reader)
        assert client.get(url).status_code == 404

    @pytest.mark.parametrize(
        ('url_name', 'kwargs'),
        [
            ('collection-personal-list-fragment', {}),
            (
                'collection-personal-city-list-fragment',
                {'pk': '00000000-0000-0000-0000-000000000001'},
            ),
        ],
    )
    def test_guest_gets_forbidden_response(
        self, client: Client, url_name: str, kwargs: dict[str, str]
    ) -> None:
        """DMR fragments персональных коллекций не перенаправляют гостя на вход."""
        response = client.get(reverse(url_name, kwargs=kwargs))

        assert response.status_code == 403

    def test_full_personal_pages_have_one_refresh_root_but_public_catalog_has_none(
        self, client: Client, personal_fragment_data: tuple[User, User, Country, Region]
    ) -> None:
        """Refresh contract ограничен каталогом владельца и списком его коллекции."""
        owner, _, country, region = personal_fragment_data
        collection = PersonalCollection.objects.create(user=owner, title='Коллекция страницы')
        create_personal_collection_city(1, country, region, collection)
        client.force_login(owner)

        catalog = client.get(reverse('collection-personal-list-view'))
        city_list = client.get(reverse('collection-personal-list', kwargs={'pk': collection.pk}))
        public_catalog = client.get(reverse('collection-personal-public-list-view'))

        assert catalog.content.decode().count('data-visited-city-refresh') == 1
        assert city_list.content.decode().count('data-visited-city-refresh') == 1
        assert 'data-visited-city-refresh' not in public_catalog.content.decode()
