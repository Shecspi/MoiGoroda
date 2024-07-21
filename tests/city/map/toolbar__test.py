"""
Тестирует корректность отображения панели со статистикой регионов.
Страница тестирования '/city/all/map'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from datetime import datetime

from bs4 import BeautifulSoup
from django.urls import reverse

from tests.create_db import (
    create_user,
    create_area,
    create_region,
    create_city,
    create_visited_city,
    create_share_settings,
    create_subscription,
)


@pytest.fixture
def setup_db(client, django_user_model):
    user1 = create_user(django_user_model, 1)
    create_user(django_user_model, 2)
    area = create_area(1)
    region = create_region(1, area[0])
    city = create_city(4, region[0])
    for i in range(3):
        create_visited_city(
            region=region[0],
            user=user1,
            city=city[i],
            date_of_visit=datetime.now(),
            has_magnet=True,
            rating=5,
        )


@pytest.mark.django_db
def test__toolbar(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'toolbar'})


@pytest.mark.django_db
def test__section__visited_cities(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-statistic'})

    assert block
    assert 'Посещено' in block.get_text()
    assert '3' in block.find('span').get_text()
    assert 'города из 4' in block.get_text()


@pytest.mark.django_db
def test__section__show_list(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-show_list'})
    button = block.find('a', {'href': reverse('city-all-list')})

    assert block
    assert button
    assert button.find('i', {'class': 'fa-solid fa-list-ol'})


@pytest.mark.django_db
def test__section__small_buttons(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-small-buttons'})

    assert block


@pytest.mark.django_db
def test__section__help(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-small-buttons'})
    button = block.find('button', {'id': 'btn_help'})

    assert button
    assert button.find('i', {'class': 'fa-regular fa-circle-question'})


@pytest.mark.django_db
def test__section__previous_year(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-small-buttons'})
    button = block.find('button', {'id': 'btn_show-visited-cities-previous-year'})

    assert button
    assert button.find('i', {'class': 'fa-solid fa-calendar-week'})


@pytest.mark.django_db
def test__section__current_year(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-small-buttons'})
    button = block.find('button', {'id': 'btn_show-visited-cities-current-year'})

    assert button
    assert button.find('i', {'class': 'fa-solid fa-calendar-days'})


@pytest.mark.django_db
def test__section__show_not_visited_cities(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-small-buttons'})
    button = block.find('button', {'id': 'btn_show-not-visited-cities'})

    assert button
    assert button.find('i', {'class': 'fa-solid fa-eye'})


@pytest.mark.django_db
def test__section__subscriptions(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-small-buttons'})
    button = block.find('button', {'id': 'btn_open_modal_with_subscriptions'})

    assert button
    assert button.find('i', {'class': 'fa-solid fa-bell'})


@pytest.mark.django_db
def test__subscriptions_button_are_disabled_if_user_has_no_subscriptions(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-small-buttons'})
    button = block.find('button', {'id': 'btn_open_modal_with_subscriptions', 'class': 'disabled'})

    assert button


@pytest.mark.django_db
def test__subscriptions_button_are_enabled_if_user_has_subscriptions(setup_db, client):
    create_share_settings(1)
    create_subscription(1, 2)
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'toolbar'}).find('div', {'id': 'section-small-buttons'})
    button = block.find('button', {'id': 'btn_open_modal_with_subscriptions', 'class': 'disabled'})

    assert not button
