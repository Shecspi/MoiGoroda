"""
Тестирует корректность отображения панели с формой поиска.
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
def setup_db__search(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')


@pytest.mark.django_db
def test__search_panel__auth_user(setup_db__search, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    panel = source.find('div', {'id': 'panel-search'})
    form = panel.find('form', {'action': reverse('region-all')})
    button = form.find('button', {'type': 'submit'})

    response_search = client.get(reverse('region-all') + '?filter=Регион+1')

    assert panel
    assert panel.find('p', {'id': 'search-active'}) is None
    assert form
    assert form.find('input', {'type': 'text'})
    assert button
    assert button.find('i', {'class': 'fa-solid fa-magnifying-glass'})
    assert 'Найти' in button.get_text()


@pytest.mark.django_db
def test__search_panel__guest(client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    panel = source.find('div', {'id': 'panel-search'})
    form = panel.find('form', {'action': reverse('region-all')})
    button = form.find('button', {'type': 'submit'})

    response_search = client.get(reverse('region-all') + '?filter=Регион+1')

    assert panel
    assert panel.find('p', {'id': 'search-active'}) is None
    assert form
    assert form.find('input', {'type': 'text'})
    assert button
    assert button.find('i', {'class': 'fa-solid fa-magnifying-glass'})
    assert 'Найти' in button.get_text()


@pytest.mark.django_db
def test__search_panel__search_active__auth_user(setup_db__search, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all') + '?filter=Регион+1')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    panel = source.find('div', {'id': 'panel-search'})
    search_active = panel.find('p', {'id': 'search-active'})
    cancel_search = search_active.find('a', {'href': reverse('region-all')})
    form = panel.find('form', {'action': reverse('region-all')})
    button = form.find('button', {'type': 'submit'})

    assert panel
    assert search_active
    assert 'Поиск по фразе' in search_active.get_text()
    assert 'Регион 1' in search_active.find('span').get_text()
    assert cancel_search
    assert 'Отменить поиск' in cancel_search.get_text()
    assert form
    assert form.find('input', {'type': 'text'})
    assert button
    assert button.find('i', {'class': 'fa-solid fa-magnifying-glass'})
    assert 'Найти' in button.get_text()


@pytest.mark.django_db
def test__htnl_has_search_panel__guest(client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    panel = source.find('div', {'id': 'panel-search'})
    form = panel.find('form', {'action': reverse('region-all')})
    button = form.find('button', {'type': 'submit'})

    assert panel
    assert form
    assert form.find('input', {'type': 'text'})
    assert button
    assert button.find('i', {'class': 'fa-solid fa-magnifying-glass'})
    assert 'Найти' in button.get_text()
