"""
Тестирует корректность отображения панели с кнопкой добавления посещённого города.
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
def setup_db(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Area 1')
    region = Region.objects.create(id=1, area=area, title='Регион 1', type='O', iso3166=f'RU-RU')


@pytest.mark.django_db
def test__html_has_add_city__auth_user(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    panel = source.find('div', {'id': 'block-add_city'})
    button = panel.find('a', {'href': reverse('city-create'), 'id': 'button-add_city'})

    assert panel
    assert button
    assert button.find('i', {'class': 'fa-solid fa-city'})
    assert 'Добавить город' in button.get_text()


@pytest.mark.django_db
def test__html_has_add_city__guest(client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    panel = source.find('div', {'id': 'block-add_city'})

    assert panel is None
