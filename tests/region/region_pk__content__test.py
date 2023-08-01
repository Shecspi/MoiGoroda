"""
Тестирует корректность отображения основного контента страницы.
Страница тестирования '/region/<pk>'.

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
def setup_db__region_pk__content_without_visited_cities(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Area 1')
    region = Region.objects.create(id=1, area=area, title=f'Регион 1', type='область', iso3166=f'RU-RU')
    for num in range(1, 40):
        City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)


@pytest.fixture
def setup_db__region_pk__content_with_visited_cities(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Area 1')
    region = Region.objects.create(id=1, area=area, title='Регион 1', type='область', iso3166=f'RU-RU')
    for num in range(1, 4):
        city = City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)
        VisitedCity.objects.create(user=user, region=region, city=city, date_of_visit='2022-01-01', rating=5)
    for i in range(4, 6):
        City.objects.create(title=f'Город {i}', region=region, coordinate_width=1, coordinate_longitude=1)


@pytest.mark.django_db
def test__pagination__1st_page__auth_user(setup_db__region_pk__content_without_visited_cities, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'block-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('button', {'id': 'link-to_first_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_prev_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 1 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination__2nd_page__auth_user(setup_db__region_pk__content_without_visited_cities, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'block-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 2 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination__3rd_page__auth_user(setup_db__region_pk__content_without_visited_cities, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?page=3')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'block-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('button', {'id': 'link-to_next_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_last_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert 'Страница 3 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination__1st_page__guest(setup_db__region_pk__content_without_visited_cities, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'block-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('button', {'id': 'link-to_first_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_prev_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 1 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination__2nd_page__guest(setup_db__region_pk__content_without_visited_cities, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'block-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 2 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination__3rd_page__guest(setup_db__region_pk__content_without_visited_cities, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?page=3')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'block-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('button', {'id': 'link-to_next_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_last_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert 'Страница 3 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__without_visited_cities__1st_page__auth_user(setup_db__region_pk__content_without_visited_cities, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    page_header = source.find('div', {'id': 'block-content'}).find('h1', {'id': 'page-header'})
    list_content = source.find('div', {'id': 'block-content'}).find('div', {'id': 'list-content'})

    assert page_header
    assert 'Регион 1 область' in page_header.get_text()
    assert list_content
    for num in range(1, 17):
        card = list_content.find('div', {'id': f'city_card_{num}'})

        assert card.find('div', {'class': 'border-success'}) is None
        assert 'Город' in card.find('div', {'class': 'h4', 'id': f'section-city_title_{num}'}).get_text()
        assert 'Население города не известно' in card.find(
            'small', {'id': f'section-population_{num}'}
        ).get_text()
        assert 'Год основания не известен' in card.find(
            'small', {'id': f'section-date_of_foundation_{num}'}
        ).get_text()


@pytest.mark.django_db
def test__without_visited_cities__2nd_page__auth_user(setup_db__region_pk__content_without_visited_cities, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    page_header = source.find('div', {'id': 'block-content'}).find('h1', {'id': 'page-header'})
    list_content = source.find('div', {'id': 'block-content'}).find('div', {'id': 'list-content'})

    assert page_header
    assert 'Регион 1 область' in page_header.get_text()
    assert list_content
    for num in range(1, 17):
        card = list_content.find('div', {'id': f'city_card_{num}'})

        assert card.find('div', {'class': 'border-success'}) is None
        assert 'Город' in card.find('div', {'class': 'h4', 'id': f'section-city_title_{num}'}).get_text()
        assert 'Население города не известно' in card.find(
            'small', {'id': f'section-population_{num}'}
        ).get_text()
        assert 'Год основания не известен' in card.find(
            'small', {'id': f'section-date_of_foundation_{num}'}
        ).get_text()


@pytest.mark.django_db
def test__without_visited_cities__3rd_page__auth_user(setup_db__region_pk__content_without_visited_cities, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?page=3')
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    page_header = source.find('div', {'id': 'block-content'}).find('h1', {'id': 'page-header'})
    list_content = source.find('div', {'id': 'block-content'}).find('div', {'id': 'list-content'})

    assert page_header
    assert 'Регион 1 область' in page_header.get_text()
    assert list_content
    for num in range(1, 8):
        card = list_content.find('div', {'id': f'city_card_{num}'})

        assert card.find('div', {'class': 'border-success'}) is None
        assert 'Город' in card.find('div', {'class': 'h4', 'id': f'section-city_title_{num}'}).get_text()
        assert 'Население города не известно' in card.find(
            'small', {'id': f'section-population_{num}'}
        ).get_text()
        assert 'Год основания не известен' in card.find(
            'small', {'id': f'section-date_of_foundation_{num}'}
        ).get_text()


@pytest.mark.django_db
def test__without_visited_cities__1st_page__guest(setup_db__region_pk__content_without_visited_cities, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    page_header = source.find('div', {'id': 'block-content'}).find('h1', {'id': 'page-header'})
    list_content = source.find('div', {'id': 'block-content'}).find('div', {'id': 'list-content'})

    assert page_header
    assert 'Регион 1 область' in page_header.get_text()
    assert list_content
    for num in range(1, 17):
        card = list_content.find('div', {'id': f'city_card_{num}'})

        assert card.find('div', {'class': 'border-success'}) is None
        assert 'Город' in card.find('div', {'class': 'h4', 'id': f'section-city_title_{num}'}).get_text()
        assert 'Население города не известно' in card.find(
            'small', {'id': f'section-population_{num}'}
        ).get_text()
        assert 'Год основания не известен' in card.find(
            'small', {'id': f'section-date_of_foundation_{num}'}
        ).get_text()


@pytest.mark.django_db
def test__without_visited_cities__2nd_page__guest(setup_db__region_pk__content_without_visited_cities, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    page_header = source.find('div', {'id': 'block-content'}).find('h1', {'id': 'page-header'})
    list_content = source.find('div', {'id': 'block-content'}).find('div', {'id': 'list-content'})

    assert page_header
    assert 'Регион 1 область' in page_header.get_text()
    assert list_content
    for num in range(1, 17):
        card = list_content.find('div', {'id': f'city_card_{num}'})

        assert card.find('div', {'class': 'border-success'}) is None
        assert 'Город' in card.find('div', {'class': 'h4', 'id': f'section-city_title_{num}'}).get_text()
        assert 'Население города не известно' in card.find(
            'small', {'id': f'section-population_{num}'}
        ).get_text()
        assert 'Год основания не известен' in card.find(
            'small', {'id': f'section-date_of_foundation_{num}'}
        ).get_text()


@pytest.mark.django_db
def test__without_visited_cities__3rd_page__guest(setup_db__region_pk__content_without_visited_cities, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?page=3')
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    page_header = source.find('div', {'id': 'block-content'}).find('h1', {'id': 'page-header'})
    list_content = source.find('div', {'id': 'block-content'}).find('div', {'id': 'list-content'})

    assert page_header
    assert 'Регион 1 область' in page_header.get_text()
    assert list_content
    for num in range(1, 8):
        card = list_content.find('div', {'id': f'city_card_{num}'})

        assert card.find('div', {'class': 'border-success'}) is None
        assert 'Город' in card.find('div', {'class': 'h4', 'id': f'section-city_title_{num}'}).get_text()
        assert 'Население города не известно' in card.find(
            'small', {'id': f'section-population_{num}'}
        ).get_text()
        assert 'Год основания не известен' in card.find(
            'small', {'id': f'section-date_of_foundation_{num}'}
        ).get_text()


@pytest.mark.django_db
def test__with_visited_cities__1st_page__auth_user(setup_db__region_pk__content_with_visited_cities, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    page_header = source.find('div', {'id': 'block-content'}).find('h1', {'id': 'page-header'})
    list_content = source.find('div', {'id': 'block-content'}).find('div', {'id': 'list-content'})

    assert page_header
    assert 'Регион 1 область' in page_header.get_text()
    assert list_content
    for num in range(1, 4):
        card = list_content.find('div', {'id': f'city_card_{num}'})

        assert card.find('div', {'class': 'border-success'})
        assert '1 января 2022 г.' in card.find('small', {'id': f'section-date_of_visit_{num}'}).get_text()
        assert 'Город' in card.find('div', {'class': 'h4', 'id': f'section-city_title_{num}'}).get_text()
        assert 'Население города не известно' in card.find(
            'small', {'id': f'section-population_{num}'}
        ).get_text()
        assert 'Год основания не известен' in card.find(
            'small', {'id': f'section-date_of_foundation_{num}'}
        ).get_text()
    for num in range(4, 6):
        card = list_content.find('div', {'id': f'city_card_{num}'})

        assert card.find('div', {'class': 'border-success'}) is None
        assert 'Город' in card.find('div', {'class': 'h4', 'id': f'section-city_title_{num}'}).get_text()
        assert 'Население города не известно' in card.find(
            'small', {'id': f'section-population_{num}'}
        ).get_text()
        assert 'Год основания не известен' in card.find(
            'small', {'id': f'section-date_of_foundation_{num}'}
        ).get_text()
