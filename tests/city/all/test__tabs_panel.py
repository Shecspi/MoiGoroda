"""
Тестирует корректность отображения панели с вкладками "Список" и "Карта".
Страница тестирования '/city/all'.

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
def test_html_has_tabs(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    tabs_panel = source.find('div', {'id': 'block-tabs'})
    button_list = tabs_panel.find('button', {'class': 'nav-link active', 'id': 'list-tab'})
    button_map = tabs_panel.find('button', {'class': 'nav-link', 'id': 'map-tab'})

    assert tabs_panel
    assert button_list
    assert 'Список' in button_list.get_text()
    assert button_list.find('i', {'class': 'fa-solid fa-list'})
    assert button_map
    assert 'Карта' in button_map.get_text()
    assert button_map.find('i', {'class': 'fa-solid fa-map-location-dot'})
