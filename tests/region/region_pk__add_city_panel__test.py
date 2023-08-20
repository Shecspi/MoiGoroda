"""
Тестирует корректность отображения блока с кнопкой добавления посещённого города.
Страница тестирования '/region/<pk>'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from bs4 import BeautifulSoup
from django.urls import reverse

from region.models import Area, Region


@pytest.fixture
def setup_db__add_city_button(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    Region.objects.create(id=1, area=area, title='Регион 1', type='область', iso3166='RU-RU1')


@pytest.mark.django_db
def test__block_add_city__auth_user(setup_db__add_city_button, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'block-add_city'})


@pytest.mark.django_db
def test__block_add_city__guest(setup_db__add_city_button, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'block-add_city'}) is None


@pytest.mark.django_db
def test__button_add_city__auth_user(setup_db__add_city_button, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    button = source.find('div', {'id': 'block-add_city'}).find('a', {'href': reverse('city-create')})

    assert button
    assert button.find('i', {'class': 'fa-solid fa-city'})
    assert 'Добавить город' in button.get_text()