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
    city_3 = City.objects.create(title='Город 3', region=region_3, coordinate_width=1, coordinate_longitude=1)
    city_4 = City.objects.create(title='Город 4', region=region_4, coordinate_width=1, coordinate_longitude=1)
    city_5 = City.objects.create(title='Город 5', region=region_4, coordinate_width=1, coordinate_longitude=1)
    VisitedCity.objects.create(
        user=user, region=region_1, city=city_1, date_of_visit="2022-01-01", has_magnet=False, rating=3
    )
    VisitedCity.objects.create(
        user=user, region=region_4, city=city_5, date_of_visit="2022-01-01", has_magnet=False, rating=3
    )


@pytest.mark.django_db
def test__statistic_panel__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'statistic_panel'})


@pytest.mark.django_db
def test__statistic_panel__guest(setup_db__statistic_panel, client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'statistic_panel'})


@pytest.mark.django_db
def test__section_total_regions__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'statistic_panel'})
    total_qty_of_regions = block.find('p', {'id': 'total_qty_of_regions'})

    assert total_qty_of_regions
    assert 'Всего регионов' in total_qty_of_regions.get_text()
    assert '4' in total_qty_of_regions.find('strong').get_text()


@pytest.mark.django_db
def test__section_total_regions__guest(setup_db__statistic_panel, client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'statistic_panel'})
    total_qty_of_regions = block.find('p', {'id': 'total_qty_of_regions'})

    assert total_qty_of_regions
    assert 'Всего регионов' in total_qty_of_regions.get_text()
    assert '4' in total_qty_of_regions.find('strong').get_text()


@pytest.mark.django_db
def test__section_visited_regions__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'statistic_panel'})
    section = block.find('p', {'id': 'qty_of_visited_regions'})

    assert section
    assert 'Посещено' in section.get_text()
    assert '2' in section.find('strong').get_text()


@pytest.mark.django_db
def test__section_visited_regions__guest(setup_db__statistic_panel, client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'statistic_panel'})
    assert block.find('p', {'id': 'qty_of_visited_regions'}) is None


@pytest.mark.django_db
def test__section_finished_regions__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'statistic_panel'})
    section = block.find('p', {'id': 'qty_of_finished_regions'})

    assert section
    assert 'Полностью' in section.get_text()
    assert '1' in section.find('strong').get_text()


@pytest.mark.django_db
def test__section_finished_regions__guest(setup_db__statistic_panel, client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'statistic_panel'})
    assert block.find('p', {'id': 'qty_of_finished_regions'}) is None


@pytest.mark.django_db
def test__section_support__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'statistic_panel'})
    section = block.find('p', {'id': 'support_link'})
    link = section.find('a', {'id': 'link_for_support_modal'})

    assert section
    assert link
    assert link.find('i', {'class': 'fa-regular fa-circle-question'})
    assert 'Подробнее...' in link.get_text()


@pytest.mark.django_db
def test__section_support__auth_user(setup_db__statistic_panel, client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'statistic_panel'})
    section = block.find('p', {'id': 'support_link'})
    link = section.find('a', {'id': 'link_for_support_modal'})

    assert section
    assert link
    assert link.find('i', {'class': 'fa-regular fa-circle-question'})
    assert 'Подробнее...' in link.get_text()
