"""
Тестирует содержимое страницы.
Страница тестирования '/'.

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
def test__main_background(client):
    response = client.get(reverse('main_page'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    section = source.find('div', {'id': 'main-background'})

    assert section
    assert 'Мои' in section.find('h1', {'id': 'index-logo'}).get_text()
    assert 'города' in section.find('h1', {'id': 'index-logo'}).get_text()
    assert section.find('h1', {'id': 'index-logo'}).find('i', {'class': 'fa-map-location-dot'})
    assert 'Вход' in section.find('a', {'href': reverse('signin')}).get_text()
    assert 'Регистрация' in section.find('a', {'href': reverse('signup')}).get_text()


@pytest.mark.django_db
def test__features(client):
    response = client.get(reverse('main_page'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    section = source.find('div', {'id': 'features'})

    assert section
    assert section.find('div', {'id': 'feature1'}).find('h1')
    assert section.find('div', {'id': 'feature1'}).find('p')
    assert section.find('div', {'id': 'feature1'}).find('img')
    assert section.find('div', {'id': 'feature2'}).find('h1')
    assert section.find('div', {'id': 'feature2'}).find('p')
    assert section.find('div', {'id': 'feature2'}).find('img')
    assert section.find('div', {'id': 'feature3'}).find('h1')
    assert section.find('div', {'id': 'feature3'}).find('p')
    assert section.find('div', {'id': 'feature3'}).find('img')


@pytest.mark.django_db
def test__footer(client):
    response = client.get(reverse('main_page'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('footer', {'id': 'section-footer'})

