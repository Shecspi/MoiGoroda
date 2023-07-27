"""
Тестирует корректность отображения основного контента страницы
Страница тестирования '/region/all'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from bs4 import BeautifulSoup

from django.db import transaction
from django.urls import reverse

from city.models import City
from region.models import Area, Region


@pytest.fixture
def setup_db(client, django_user_model):
    """
    Создаёт 20 записей в таблице 'Region' и 20 в 'City' (все с 1 регионом).
    """
    django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Area 1')
    for num in range(1, 21):
        region = Region.objects.create(area=area, title=f'Регион {num}', type='область', iso3166=f'RU-RU-{num}')
        City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)


@pytest.mark.django_db
def test__zero_visited_regions__1st_page__auth_user(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    page_header = source.find('h1', {'id': 'page-header'})
    list_content = source.find('div', {'id': 'list-content'})
    all_regions = list_content.find_all('div', {'class': 'region_card'})
    pagination_panel = list_content.find('div', {'id': 'pagination-panel'})

    assert page_header
    assert 'Регионы России' in page_header.get_text()
    assert list_content
    assert len(all_regions) == 16
    for region in all_regions:
        assert 'Area 1 федеральный округ' in region.get_text()
        assert 'Регион ' in region.find('a').get_text()
        assert '0 из 1' in region.get_text()
        assert region.find('div', {'class': 'progress'}) is None
    assert pagination_panel
    assert 'Страница 1 из 2' in source.find('div', {'id': 'pagination-panel'}).get_text()


@pytest.mark.django_db
def test__zero_visited_regions__1st_page__guest(setup_db, client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    page_header = source.find('h1', {'id': 'page-header'})
    list_content = source.find('div', {'id': 'list-content'})
    all_regions = source.find_all('div', {'class': 'region_card'})
    pagination_panel = source.find('div', {'id': 'pagination-panel'})

    assert page_header
    assert 'Регионы России' in page_header.get_text()
    assert list_content
    assert len(all_regions) == 16
    for region in all_regions:
        assert 'Area 1 федеральный округ' in region.get_text()
        assert 'Регион ' in region.find('a').get_text()
        assert 'Всего городов: 1' in region.get_text()
        assert region.find('div', {'class': 'progress'}) is None
    assert pagination_panel
    assert 'Страница 1 из 2' in source.find('div', {'id': 'pagination-panel'}).get_text()


@pytest.mark.django_db
def test__zero_visited_regions__2nd_page__auth_user(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all') + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    page_header = source.find('h1', {'id': 'page-header'})
    list_content = source.find('div', {'id': 'list-content'})
    all_regions = source.find_all('div', {'class': 'region_card'})
    pagination_panel = source.find('div', {'id': 'pagination-panel'})

    assert page_header
    assert 'Регионы России' in page_header.get_text()
    assert list_content
    assert len(all_regions) == 4
    for region in all_regions:
        assert 'Area 1 федеральный округ' in region.get_text()
        assert 'Регион ' in region.find('a').get_text()
        assert '0 из 1' in region.get_text()
        assert region.find('div', {'class': 'pregress-bar'}) is None
    assert pagination_panel
    assert 'Страница 2 из 2' in source.find('div', {'id': 'pagination-panel'}).get_text()


@pytest.mark.django_db
def test__zero_visited_regions__2nd_page__guest(setup_db, client):
    response = client.get(reverse('region-all') + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    page_header = source.find('h1', {'id': 'page-header'})
    list_content = source.find('div', {'id': 'list-content'})
    all_regions = source.find_all('div', {'class': 'region_card'})
    pagination_panel = source.find('div', {'id': 'pagination-panel'})

    assert page_header
    assert 'Регионы России' in page_header.get_text()
    assert list_content
    assert len(all_regions) == 4
    for region in all_regions:
        assert 'Area 1 федеральный округ' in region.get_text()
        assert 'Регион ' in region.find('a').get_text()
        assert 'Всего городов: 1' in region.get_text()
        assert region.find('div', {'class': 'pregress-bar'}) is None
    assert pagination_panel
    assert 'Страница 2 из 2' in source.find('div', {'id': 'pagination-panel'}).get_text()
