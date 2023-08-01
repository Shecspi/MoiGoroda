"""
Тестирует корректность отображения панели с вкладками "Список" и "Карта".
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
def setup_db__tabs_panel(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')


@pytest.mark.django_db
def test__block_tabs__auth_user(setup_db__tabs_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'tabs_panel'})


@pytest.mark.django_db
def test__block_tabs__guest(setup_db__tabs_panel, client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'tabs_panel'})


@pytest.mark.django_db
def test__button_list__auth_user(setup_db__tabs_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    button = source.find('div', {'id': 'tabs_panel'}).find('button', {'class': 'nav-link active', 'id': 'list-tab'})

    assert button
    assert 'Список' in button.get_text()
    assert button.find('i', {'class': 'fa-solid fa-list'})


@pytest.mark.django_db
def test__button_list__guest(setup_db__tabs_panel, client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    button = source.find('div', {'id': 'tabs_panel'}).find('button', {'class': 'nav-link active', 'id': 'list-tab'})

    assert button
    assert 'Список' in button.get_text()
    assert button.find('i', {'class': 'fa-solid fa-list'})


@pytest.mark.django_db
def test__button_map__auth_user(setup_db__tabs_panel, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    button = source.find('div', {'id': 'tabs_panel'}).find('button', {'class': 'nav-link', 'id': 'map-tab'})

    assert button
    assert 'Карта' in button.get_text()
    assert button.find('i', {'class': 'fa-solid fa-map-location-dot'})


@pytest.mark.django_db
def test__button_map__guest(setup_db__tabs_panel, client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    button = source.find('div', {'id': 'tabs_panel'}).find('button', {'class': 'nav-link', 'id': 'map-tab'})

    assert button
    assert 'Карта' in button.get_text()
    assert button.find('i', {'class': 'fa-solid fa-map-location-dot'})
