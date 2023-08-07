"""
Тестирует корректность отображения панели со статистикой регионов.
Страница тестирования '/region/all'.

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
def setup_db__statistic_panel(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region_1 = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    region_2 = Region.objects.create(area=area, title='Регион 2', type='область', iso3166='RU-RU2')
    region_3 = Region.objects.create(area=area, title='Регион 3', type='область', iso3166='RU-RU3')
    region_4 = Region.objects.create(area=area, title='Регион 4', type='область', iso3166='RU-RU4')
    city_1 = City.objects.create(title='Город 1', region=region_1, coordinate_width=1, coordinate_longitude=1)
    city_2 = City.objects.create(title='Город 2', region=region_2, coordinate_width=1, coordinate_longitude=1)
    VisitedCity.objects.create(
        user=user, region=region_1, city=city_1, date_of_visit="2022-01-01", has_magnet=False, rating=3
    )
    VisitedCity.objects.create(
        user=user, region=region_4, city=city_2, date_of_visit="2022-01-01", has_magnet=False, rating=3
    )


@pytest.mark.django_db
def test__statistic_panel__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'block-statistic'})


@pytest.mark.django_db
def test__statistic_panel__guest(setup_db__statistic_panel, client):
    response = client.get(reverse('region-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'block-statistic'})


@pytest.mark.django_db
def test__section_total_regions__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'block-statistic'})

    assert 'Посещено' in block.get_text()
    assert '2' in block.find('span').get_text()
    assert 'региона из 4' in block.get_text()


@pytest.mark.django_db
def test__section_total_regions__guest(setup_db__statistic_panel, client):
    response = client.get(reverse('region-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'block-statistic'})

    assert 'В России' in block.get_text()
    assert '4' in block.find('span').get_text()
    assert 'регионов' in block.get_text()
