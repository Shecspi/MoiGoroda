"""
Тестирует корректность отображения вспомогательного окна с подробным описанием панели статистики.
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
def setup_db__region_pk__modal_window(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    Region.objects.create(id=1, area=area, title='Регион 1', type='область', iso3166='RU-RU')


@pytest.mark.django_db
def test__html_has_modal_window__auth_user(setup_db__region_pk__modal_window, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    window = source.find('div', {'id': 'window-details'})
    header = window.find('div', {'class': 'modal-header'})
    body = window.find('div', {'class': 'modal-body'})

    assert window
    assert header
    assert 'Подробнее' in header.find('h5', {'class': 'modal-title', 'id': 'window-title'}).get_text()
    assert header.find('button', {'class': 'btn-close'})
    assert body
    assert 'Всего городов' in body.find('p', {'id': 'section-modal-total_cities'}).find('strong').get_text()
    assert 'Посещено' in body.find('p', {'id': 'section-modal-visited'}).find('strong').get_text()
    assert 'В этом году' in body.find('p', {'id': 'section-modal-current_year'}).find('strong').get_text()
    assert 'В прошлом году' in body.find('p', {'id': 'section-modal-last_year'}).find('strong').get_text()


@pytest.mark.django_db
def test__html_has_modal_window__guest(setup_db__region_pk__modal_window, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    window = source.find('div', {'id': 'window-details'})
    header = window.find('div', {'class': 'modal-header'})
    body = window.find('div', {'class': 'modal-body'})

    assert window
    assert header
    assert 'Подробнее' in header.find('h5', {'class': 'modal-title', 'id': 'window-title'}).get_text()
    assert header.find('button', {'class': 'btn-close'})
    assert body
    assert 'Всего городов' in body.find('p', {'id': 'section-modal-total_cities'}).find('strong').get_text()
    assert body.find('p', {'id': 'section-modal-visited'}) is None
    assert body.find('p', {'id': 'section-modal-current_year'}) is None
    assert body.find('p', {'id': 'section-modal-last_year'}) is None
