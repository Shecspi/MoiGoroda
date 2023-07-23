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
def setup_db(client, django_user_model):
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
def test__statistic_panel_for_auth_user(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    statistic_panel = source.find('div', {'id': 'statistic_panel'})
    total_qty_of_regions = statistic_panel.find('p', {'id': 'total_qty_of_regions'})
    qty_of_visited_regions = statistic_panel.find('p', {'id': 'qty_of_visited_regions'})
    qty_of_finished_regions = statistic_panel.find('p', {'id': 'qty_of_finished_regions'})
    support_link = statistic_panel.find('p', {'id': 'support_link'})
    link_for_support_modal = support_link.find('a', {'id': 'link_for_support_modal'})

    assert statistic_panel
    assert total_qty_of_regions
    assert 'Всего регионов' in total_qty_of_regions.get_text()
    assert '4' in total_qty_of_regions.find('strong').get_text()
    assert qty_of_visited_regions
    assert 'Посещено' in qty_of_visited_regions.get_text()
    assert '2' in qty_of_visited_regions.find('strong').get_text()
    assert qty_of_finished_regions
    assert 'Полностью' in qty_of_finished_regions.get_text()
    assert '1' in qty_of_finished_regions.find('strong').get_text()
    assert support_link
    assert link_for_support_modal
    assert link_for_support_modal.find('i', {'class': 'fa-regular fa-circle-question'})
    assert support_link and 'Подробнее...' in support_link.get_text()


@pytest.mark.django_db
def test__statistic_panel_for_guest(setup_db, client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    statistic_panel = source.find('div', {'id': 'statistic_panel'})
    total_qty_of_regions = statistic_panel.find('p', {'id': 'total_qty_of_regions'})
    qty_of_visited_regions = statistic_panel.find('p', {'id': 'qty_of_visited_regions'})
    qty_of_finished_regions = statistic_panel.find('p', {'id': 'qty_of_finished_regions'})
    support_link = statistic_panel.find('p', {'id': 'support_link'})
    link_for_support_modal = support_link.find('a', {'id': 'link_for_support_modal'})

    assert statistic_panel
    assert total_qty_of_regions
    assert 'Всего регионов' in total_qty_of_regions.get_text()
    assert '4' in total_qty_of_regions.find('strong').get_text()
    assert qty_of_visited_regions is None
    assert qty_of_finished_regions is None
    assert support_link
    assert link_for_support_modal
    assert link_for_support_modal.find('i', {'class': 'fa-regular fa-circle-question'})
    assert support_link and 'Подробнее...' in support_link.get_text()
