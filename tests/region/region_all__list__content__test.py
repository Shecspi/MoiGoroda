"""
Тестирует корректность отображения основного контента страницы.
Страница тестирования '/region/all/list'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from bs4 import BeautifulSoup

from django.urls import reverse

from city.models import City, VisitedCity
from region.models import Area, Region


@pytest.fixture
def setup_db__content_without_visited_regions__region_all(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Area 1')
    for num in range(1, 40):
        region = Region.objects.create(area=area, title=f'Регион {num}', type='область', iso3166=f'RU-RU-{num}')
        City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)


@pytest.fixture
def setup_db__content_with_visited_regions__region_all(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Area 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166=f'RU-RU')
    for num in range(1, 4):
        city = City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)
        VisitedCity.objects.create(user=user, region=region, city=city, rating=5)
    for i in range(4, 6):
        City.objects.create(title=f'Город {i}', region=region, coordinate_width=1, coordinate_longitude=1)


@pytest.mark.django_db
def test__pagination__1st_page__auth_user(setup_db__content_without_visited_regions__region_all, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'section-content'}).find('div', {'id': 'section-pagination'})

    assert pagination
    assert pagination.find('button', {'id': 'link-to_first_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_prev_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 1 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination__2nd_page__auth_user(setup_db__content_without_visited_regions__region_all, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all-list') + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'section-content'}).find('div', {'id': 'section-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 2 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination__3rd_page__auth_user(setup_db__content_without_visited_regions__region_all, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all-list') + '?page=3')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'section-content'}).find('div', {'id': 'section-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('button', {'id': 'link-to_next_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_last_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert 'Страница 3 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination__1st_page__guest(setup_db__content_without_visited_regions__region_all, client):
    response = client.get(reverse('region-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'section-content'}).find('div', {'id': 'section-pagination'})

    assert pagination
    assert pagination.find('button', {'id': 'link-to_first_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_prev_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 1 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination__2nd_page__guest(setup_db__content_without_visited_regions__region_all, client):
    response = client.get(reverse('region-all-list') + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'section-content'}).find('div', {'id': 'section-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 2 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination__3rd_page__guest(setup_db__content_without_visited_regions__region_all, client):
    response = client.get(reverse('region-all-list') + '?page=3')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'section-content'}).find('div', {'id': 'section-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('button', {'id': 'link-to_next_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_last_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert 'Страница 3 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__without_visited_regions__1st_page__auth_user(setup_db__content_without_visited_regions__region_all, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    page_header = content.find('h1', {'id': 'section-page-header'})

    assert content
    assert page_header
    assert 'Список регионов России' in page_header.get_text()
    for num in range(1, 17):
        card = content.find('div', {'id': f'region_card_{num}'})
        assert 'Регион' in card.find('h4', {'id': f'section-region_title_{num}'}).get_text()
        assert 'Area 1' in card.find('div', {'id': f'section-area_title_{num}'}).get_text()
        assert '0 из 1' in card.find('div', {'id': f'section-qty_of_cities_{num}'}).get_text()
        assert card.find('div', {'id': f'section-qty_of_cities_{num}'}).find(
            'div', {'id': f'progress_bar_{num}'}
        ) is None


@pytest.mark.django_db
def test__without_visited_regions__2nd_page__auth_user(setup_db__content_without_visited_regions__region_all, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all-list') + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    page_header = content.find('h1', {'id': 'section-page-header'})

    assert content
    assert page_header
    assert 'Список регионов России' in page_header.get_text()
    for num in range(1, 17):
        card = content.find('div', {'id': f'region_card_{num}'})
        assert 'Регион' in card.find('h4', {'id': f'section-region_title_{num}'}).get_text()
        assert 'Area 1' in card.find('div', {'id': f'section-area_title_{num}'}).get_text()
        assert '0 из 1' in card.find('div', {'id': f'section-qty_of_cities_{num}'}).get_text()
        assert card.find('div', {'id': f'section-qty_of_cities_{num}'}).find(
            'div', {'id': f'progress_bar_{num}'}
        ) is None


@pytest.mark.django_db
def test__without_visited_regions__3rd_page__auth_user(setup_db__content_without_visited_regions__region_all, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all-list') + '?page=3')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    page_header = content.find('h1', {'id': 'section-page-header'})

    assert content
    assert page_header
    assert 'Список регионов России' in page_header.get_text()
    for num in range(1, 8):
        card = content.find('div', {'id': f'region_card_{num}'})
        assert f'Регион' in card.find('h4', {'id': f'section-region_title_{num}'}).get_text()
        assert 'Area 1' in card.find('div', {'id': f'section-area_title_{num}'}).get_text()
        assert '0 из 1' in card.find('div', {'id': f'section-qty_of_cities_{num}'}).get_text()
        assert card.find('div', {'id': f'section-qty_of_cities_{num}'}).find(
            'div', {'id': f'progress_bar_{num}'}
        ) is None


@pytest.mark.django_db
def test__without_visited_regions__1st_page__guest(setup_db__content_without_visited_regions__region_all, client):
    response = client.get(reverse('region-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    page_header = content.find('h1', {'id': 'section-page-header'})

    assert content
    assert page_header
    assert 'Список регионов России' in page_header.get_text()
    for num in range(1, 17):
        card = content.find('div', {'id': f'region_card_{num}'})
        assert f'Регион' in card.find('h4', {'id': f'section-region_title_{num}'}).get_text()
        assert 'Area 1' in card.find('div', {'id': f'section-area_title_{num}'}).get_text()
        assert 'Всего городов: 1' in card.find('div', {'id': f'section-qty_of_cities_{num}'}).get_text()
        assert card.find('div', {'id': f'section-qty_of_cities_{num}'}).find(
            'div', {'id': f'progress_bar_{num}'}
        ) is None


@pytest.mark.django_db
def test__without_visited_regions__2nd_page__guest(setup_db__content_without_visited_regions__region_all, client):
    response = client.get(reverse('region-all-list') + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    page_header = content.find('h1', {'id': 'section-page-header'})

    assert content
    assert page_header
    assert 'Список регионов России' in page_header.get_text()
    for num in range(1, 17):
        card = content.find('div', {'id': f'region_card_{num}'})
        assert f'Регион' in card.find('h4', {'id': f'section-region_title_{num}'}).get_text()
        assert 'Area 1' in card.find('div', {'id': f'section-area_title_{num}'}).get_text()
        assert 'Всего городов: 1' in card.find('div', {'id': f'section-qty_of_cities_{num}'}).get_text()
        assert card.find('div', {'id': f'section-qty_of_cities_{num}'}).find(
            'div', {'id': f'progress_bar_{num}'}
        ) is None


@pytest.mark.django_db
def test__without_visited_regions__3rd_page__guest(setup_db__content_without_visited_regions__region_all, client):
    response = client.get(reverse('region-all-list') + '?page=3')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    page_header = content.find('h1', {'id': 'section-page-header'})

    assert content
    assert page_header
    assert 'Список регионов России' in page_header.get_text()
    for num in range(1, 8):
        card = content.find('div', {'id': f'region_card_{num}'})
        assert f'Регион' in card.find('h4', {'id': f'section-region_title_{num}'}).get_text()
        assert 'Area 1' in card.find('div', {'id': f'section-area_title_{num}'}).get_text()
        assert 'Всего городов: 1' in card.find('div', {'id': f'section-qty_of_cities_{num}'}).get_text()
        assert card.find('div', {'id': f'section-qty_of_cities_{num}'}).find(
            'div', {'id': f'progress_bar_{num}'}
        ) is None


@pytest.mark.django_db
def test__with_visited_regions__1st_page__auth_user(setup_db__content_with_visited_regions__region_all, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    page_header = content.find('h1', {'id': 'section-page-header'})

    assert content
    assert page_header
    assert 'Список регионов России' in page_header.get_text()
    card = content.find('div', {'id': f'region_card_1'})
    assert 'Регион' in card.find('h4', {'id': f'section-region_title_1'}).get_text()
    assert 'Area 1' in card.find('div', {'id': f'section-area_title_1'}).get_text()
    assert '3 из 5' in card.find('div', {'id': f'section-qty_of_cities_1'}).get_text()
    assert card.find(
        'div', {'id': f'section-qty_of_cities_1'}
    ).find('div', {'id': 'progress_bar_1', 'style': 'width: 60%', 'aria-valuenow': '60'})
