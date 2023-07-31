"""
Тестирует корректность отображения контента с карточками посещённых городоов.
Страница тестирования '/city/all'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from datetime import datetime

from bs4 import BeautifulSoup
from django.urls import reverse

from city.models import City, VisitedCity
from region.models import Area, Region


@pytest.fixture
def setup_db__content_for_pagination(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    for num in range(1, 40):
        city = City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)
        VisitedCity.objects.create(
            user=user, region=region, city=city, date_of_visit=f"{datetime.now().year - num}-01-01", has_magnet=False, rating=3
        )


@pytest.mark.django_db
def test__content(setup_db__content_for_pagination, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'block-content'})

    assert source.find('nav', {'id': 'block-header'})
    assert source.find('footer', {'id': 'block-footer'})
    assert content


@pytest.mark.django_db
def test__pagination_first_page(setup_db__content_for_pagination, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'block-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('button', {'id': 'link-to_first_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_prev_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 1 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination_second_page(setup_db__content_for_pagination, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all') + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'block-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 2 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination_third_page(setup_db__content_for_pagination, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all') + '?page=3')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'block-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('button', {'id': 'link-to_next_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_last_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert 'Страница 3 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()
