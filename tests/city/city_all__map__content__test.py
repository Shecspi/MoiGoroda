"""
Тестирует корректность отображения карты с отмеченными посещёнными городами.
Страница тестирования '/city/all/map'.

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
    for num in range(1, 3):
        city = City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)
        VisitedCity.objects.create(
            user=user, region=region, city=city, has_magnet=False, rating=3
        )


@pytest.mark.django_db
def test__content(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'block-content'})

    assert source.find('h1', {'id': 'block-page_header'})
    assert source.find('div', {'id': 'side_nav'})
    assert source.find('div', {'id': 'block-content'})
    assert source.find('footer', {'id': 'block-footer'})
    assert content


@pytest.mark.django_db
def test__map(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'block-content'}).find('div', {'id': 'map'})
