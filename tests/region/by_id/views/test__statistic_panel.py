"""
Тестирует корректность отображения панели со статистикой регионов.
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
def setup_db(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    city_1 = City.objects.create(title='Город 1', region=region, coordinate_width=1, coordinate_longitude=1)
    city_2 = City.objects.create(title='Город 2', region=region, coordinate_width=1, coordinate_longitude=1)
    city_3 = City.objects.create(title='Город 3', region=region, coordinate_width=1, coordinate_longitude=1)
    city_4 = City.objects.create(title='Город 4', region=region, coordinate_width=1, coordinate_longitude=1)
    city_5 = City.objects.create(title='Город 5', region=region, coordinate_width=1, coordinate_longitude=1)
    VisitedCity.objects.create(
        user=user, region=region, city=city_1, date_of_visit=f"{datetime.now().year}-01-01", has_magnet=False, rating=3
    )
    VisitedCity.objects.create(
        user=user, region=region, city=city_2, date_of_visit=f"{datetime.now().year}-01-01", has_magnet=False, rating=3
    )
    VisitedCity.objects.create(
        user=user, region=region, city=city_3, date_of_visit="2022-01-01", has_magnet=False, rating=3
    )


@pytest.mark.django_db
def test__statistic_panel_for_auth_user(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block_statistic = source.find('div', {'id': 'block-statistic'})
    text_qty_of_cities_in_region = block_statistic.find('p', {'id': 'text-total_cities_in_region'})
    text_qty_of_visited_cities = block_statistic.find('p', {'id': 'text-qty_of_visited_cities'})
    text_qty_of_visiteid_cities_this_year = block_statistic.find('p', {'id': 'text-qty_of_visited_cities_this_year'})
    text_support = block_statistic.find('p', {'id': 'text-support'})
    link_support = text_support.find('a', {'id': 'link-support'})

    assert block_statistic
    assert text_qty_of_cities_in_region
    assert 'Городов в регионе:' in text_qty_of_cities_in_region.get_text()
    assert '5' in text_qty_of_cities_in_region.find('strong').get_text()
    assert text_qty_of_visited_cities
    assert 'Посещено' in text_qty_of_visited_cities.get_text()
    assert '3' in text_qty_of_visited_cities.find('strong').get_text()
    assert text_qty_of_visiteid_cities_this_year
    assert 'В этом году' in text_qty_of_visiteid_cities_this_year.get_text()
    assert '2' in text_qty_of_visiteid_cities_this_year.find('strong').get_text()
    assert text_support
    assert text_support and 'Подробнее...' in text_support.get_text()
    assert link_support
    assert link_support.find('i', {'class': 'fa-regular fa-circle-question'})


@pytest.mark.django_db
def test__statistic_panel_for_guest(setup_db, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block_statistic = source.find('div', {'id': 'block-statistic'})
    text_qty_of_cities_in_region = block_statistic.find('p', {'id': 'text-total_cities_in_region'})
    text_support = block_statistic.find('p', {'id': 'text-support'})
    link_support = text_support.find('a', {'id': 'link-support'})

    assert block_statistic
    assert text_qty_of_cities_in_region
    assert 'Городов в регионе:' in text_qty_of_cities_in_region.get_text()
    assert '5' in text_qty_of_cities_in_region.find('strong').get_text()
    assert text_support
    assert text_support and 'Подробнее...' in text_support.get_text()
    assert link_support
    assert link_support.find('i', {'class': 'fa-regular fa-circle-question'})
