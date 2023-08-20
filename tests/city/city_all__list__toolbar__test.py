"""
Тестирует корректность отображения панели со статистикой городов.
Страница тестирования '/city/all/list'.

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
def setup_db(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    city_1 = City.objects.create(title='Город 1', region=region, coordinate_width=1, coordinate_longitude=1)
    city_2 = City.objects.create(title='Город 2', region=region, coordinate_width=1, coordinate_longitude=1)
    city_3 = City.objects.create(title='Город 3', region=region, coordinate_width=1, coordinate_longitude=1)
    city_4 = City.objects.create(title='Город 4', region=region, coordinate_width=1, coordinate_longitude=1)
    VisitedCity.objects.create(
        user=user, region=region, city=city_1, date_of_visit=f"{datetime.now().year}-01-01", has_magnet=False, rating=3
    )
    VisitedCity.objects.create(
        user=user, region=region, city=city_2, date_of_visit=f"{datetime.now().year - 1}-01-01", has_magnet=False, rating=3
    )
    VisitedCity.objects.create(
        user=user, region=region, city=city_2, date_of_visit=f"{datetime.now().year - 1}-01-01", has_magnet=False, rating=3
    )


@pytest.mark.django_db
def test__toolbar(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'toolbar'})


@pytest.mark.django_db
def test__section__visited_cities(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'block-statistic'})

    assert block
    assert 'Посещено' in block.get_text()
    assert '3' in block.find('span').get_text()
    assert 'города из 4' in block.get_text()


@pytest.mark.django_db
def test__section__show_map(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-show_map'})
    button = block.find('a', {'href': reverse('city-all-map')})

    assert block
    assert button
    assert button.find('i', {'class': 'fa-solid fa-map-location-dot'})
    assert 'Посмотреть на карте' in button.get_text()


@pytest.mark.django_db
def test__section__filtering(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-filter'})
    button = block.find('a', {'id': 'open_filter_toolbar'})

    assert block
    assert button
    assert button.find('i', {'class': 'fa-solid fa-filter'})
    assert 'Фильтры' in button.get_text()


@pytest.mark.django_db
def test__section__sorting(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-sorting'})
    button = block.find('a', {'id': 'open_sorting_toolbar'})

    assert block
    assert button
    assert button.find('i', {'class': 'fa-solid fa-sort'})
    assert 'Сортировка' in button.get_text()

