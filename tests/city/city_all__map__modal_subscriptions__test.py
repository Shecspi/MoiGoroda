"""
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
def test__page_has_modal_subscriptions(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'subscriptions_modal_window'})

    assert block


@pytest.mark.django_db
def test__modal_help_has_title(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'subscriptions_modal_window'})
    title_block = block.find('div', {'class': 'modal-header'})
    title = title_block.find('h1', {'id': 'subscriptions_modal_label'})
    icon = title.find('i', {'class': 'fa-solid fa-bell'})

    assert title
    assert icon
    assert 'Ваши подписки' in title.get_text()


@pytest.mark.django_db
def test__modal_help_has_footer_with_buttons(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'subscriptions_modal_window'})
    footer_block = block.find('div', {'class': 'modal-footer'})
    close_button = footer_block.find('button', {'class': 'btn btn-secondary btn-sm'})
    apply_button = footer_block.find('button', {'class': 'btn btn-success'})

    assert footer_block
    assert close_button
    assert 'Закрыть' in close_button.get_text()
    assert apply_button
    assert 'Применить' in apply_button.get_text()


@pytest.mark.django_db
def test__modal_help_has_list_of_subscriptions(setup_db, client):
    create_share_settings(1)
    create_subscription(1, 2)
    client.login(username='username1', password='password')
    response = client.get(reverse('city-all-map'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'class': 'modal-body'})
    subscription_section = block.find('div', {'class': 'list-group'})
    subscription_input = subscription_section.find(
        'input',
        {
            'class': 'form-check-input checkbox_username',
            'type': 'checkbox',
            'name': 'users',
            'value': '2',
        },
    )
    subscription_label = subscription_section.find('label', {'class': 'form-check-label mx-3'})

    assert subscription_section
    assert subscription_input
    assert subscription_label
    assert 'username2   ' in subscription_label.get_text()
