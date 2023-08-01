"""
Тестирует корректность отображения панели со статистикой региона.
Страница тестирования '/region/<pk>'.

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
def setup_db__statistic_panel(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(id=1, area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    city_1 = City.objects.create(title='Город 1', region=region, coordinate_width=1, coordinate_longitude=1)
    city_2 = City.objects.create(title='Город 2', region=region, coordinate_width=1, coordinate_longitude=1)
    city_3 = City.objects.create(title='Город 3', region=region, coordinate_width=1, coordinate_longitude=1)
    city_4 = City.objects.create(title='Город 4', region=region, coordinate_width=1, coordinate_longitude=1)
    VisitedCity.objects.create(
        user=user, region=region, city=city_1,
        date_of_visit=f'{datetime.now().year}-01-01', has_magnet=False, rating=3
    )
    VisitedCity.objects.create(
        user=user, region=region, city=city_2,
        date_of_visit=f'{datetime.now().year}-01-01', has_magnet=False, rating=3
    )
    VisitedCity.objects.create(
        user=user, region=region, city=city_3,
        date_of_visit=f'{datetime.now().year - 1}-01-01', has_magnet=False, rating=3
    )


@pytest.mark.django_db
def test__block_statistic__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'block-statistic'})


@pytest.mark.django_db
def test__block_statistic__guest(setup_db__statistic_panel, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'block-statistic'})


@pytest.mark.django_db
def test__section_total_regions__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    section = source.find('div', {'id': 'block-statistic'}).find('p', {'id': 'section-statistic-total_qty_of_cities'})

    assert section
    assert 'Городов в регионе:' in section.get_text()
    assert '4' in section.find('strong').get_text()


@pytest.mark.django_db
def test__section_total_regions__guest(setup_db__statistic_panel, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    section = source.find('div', {'id': 'block-statistic'}).find('p', {'id': 'section-statistic-total_qty_of_cities'})

    assert section
    assert 'Городов в регионе:' in section.get_text()
    assert '4' in section.find('strong').get_text()


@pytest.mark.django_db
def test__section_visited_cities__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    section = source.find('div', {'id': 'block-statistic'}).find('p', {'id': 'section-statistic-qty_of_visited_cities'})

    assert section
    assert 'Посещено' in section.get_text()
    assert '3' in section.find('strong').get_text()


@pytest.mark.django_db
def test__section_visited_cities__guest(setup_db__statistic_panel, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'block-statistic'}).find(
        'p', {'id': 'section-statistic-qty_of_visited_cities'}
    ) is None


@pytest.mark.django_db
def test__section_visited_cities_current_year__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    section = source.find('div', {'id': 'block-statistic'}).find(
        'p', {'id': 'section-statistic-qty_of_finished_regions'}
    )

    assert section
    assert 'В этом году:' in section.get_text()
    assert '2' in section.find('strong').get_text()


@pytest.mark.django_db
def test__section_visited_cities_current_year__guest(setup_db__statistic_panel, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'block-statistic'}).find(
        'p', {'id': 'section-statistic-qty_of_finished_regions'}
    ) is None


@pytest.mark.django_db
def test__section_support__auth_user(setup_db__statistic_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'block-statistic'})
    section = block.find('p', {'id': 'section-statistic-support'})
    link = section.find('a', {'id': 'link-statistic-support'})

    assert section
    assert link
    assert link.find('i', {'class': 'fa-regular fa-circle-question'})
    assert 'Подробнее...' in link.get_text()


@pytest.mark.django_db
def test__section_support__auth_user(setup_db__statistic_panel, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'block-statistic'})
    section = block.find('p', {'id': 'section-statistic-support'})
    link = section.find('a', {'id': 'link-statistic-support'})

    assert section
    assert link
    assert link.find('i', {'class': 'fa-regular fa-circle-question'})
    assert 'Подробнее...' in link.get_text()
