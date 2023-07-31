"""
Тестирует корректность отображения панели с кнопкой добавления посещённого города.
Страница тестирования '/region/all'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from bs4 import BeautifulSoup
from django.urls import reverse


@pytest.fixture
def setup_db(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')


@pytest.mark.django_db
def test__html_has_add_city__auth_user(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    panel = source.find('div', {'id': 'panel-add_city'})
    button = panel.find('a', {'href': reverse('city-create')})

    assert panel
    assert button
    assert button.find('i', {'class': 'fa-solid fa-city'})
    assert 'Добавить город' in button.get_text()


@pytest.mark.django_db
def test__html_has_add_city__guest(client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    panel = source.find('div', {'id': 'panel-add_city'})

    assert panel is None