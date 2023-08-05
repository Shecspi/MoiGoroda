"""
Тестирует корректность отображения вспомогательного окна с подробным описанием панели статистики.
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
def test__html_has_modal_window__auth_user(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    modal_window = source.find('div', {'id': 'detailsModal'})
    header = modal_window.find('div', {'class': 'modal-header'})
    body = modal_window.find('div', {'class': 'modal-body'})

    assert modal_window
    assert header
    assert 'Подробнее' in header.find('h5', {'class': 'modal-title'}).get_text()
    assert header.find('button', {'class': 'btn-close'})
    assert body
    assert 'Всего регионов' in body.find('p', {'id': 'modal-total_regions'}).find('strong').get_text()
    assert 'Посещено' in body.find('p', {'id': 'modal-visited_regions'}).find('strong').get_text()
    assert 'Полностью' in body.find('p', {'id': 'modal-finished_regions'}).find('strong').get_text()


@pytest.mark.django_db
def test__html_has_modal_window__guest(setup_db, client):
    response = client.get(reverse('region-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    modal_window = source.find('div', {'id': 'detailsModal'})
    header = modal_window.find('div', {'class': 'modal-header'})
    body = modal_window.find('div', {'class': 'modal-body'})

    assert modal_window
    assert header
    assert 'Подробнее' in header.find('h5', {'class': 'modal-title'}).get_text()
    assert header.find('button', {'class': 'btn-close'})
    assert body
    assert 'Всего регионов' in body.find('p', {'id': 'modal-total_regions'}).find('strong').get_text()
    assert body.find('p', {'id': 'modal-visited_regions'}) is None
    assert body.find('p', {'id': 'modal-finished_regions'}) is None
