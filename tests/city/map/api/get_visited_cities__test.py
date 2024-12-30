"""
----------------------------------------------

Copyright Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import json

import pytest
from datetime import datetime

from django.urls import reverse

from tests.create_db import (
    create_user,
    create_area,
    create_region,
    create_city,
    create_visited_city,
    create_superuser,
)


@pytest.fixture
def setup_db_without_visited_cities(client, django_user_model):
    create_user(django_user_model, 1)
    create_user(django_user_model, 2)
    create_superuser(django_user_model, 3)
    area = create_area(1)
    region = create_region(1, area[0])
    create_city(4, region[0])


@pytest.fixture
def setup_db_with_visited_cities(client, django_user_model):
    user1 = create_user(django_user_model, 1)
    user2 = create_user(django_user_model, 2)
    create_superuser(django_user_model, 3)
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
    create_visited_city(
        region=region[0],
        user=user2,
        city=city[3],
        date_of_visit=datetime.now(),
        has_magnet=True,
        rating=5,
    )


def access_by_POST_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.post(reverse('api__get_visited_cities'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited'
    assert response.status_code == 405


def access_by_DELETE_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.delete(reverse('api__get_visited_cities'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited'
    assert response.status_code == 405


def access_by_PUT_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.put(reverse('api__get_visited_cities'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited'
    assert response.status_code == 405


def access_by_PATCH_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.patch(reverse('api__get_visited_cities'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited'
    assert response.status_code == 405


def guest_can_not_get_visited_cities__test(setup_db_without_visited_cities, caplog, client):
    response = client.get(reverse('api__get_visited_cities'))

    assert caplog.records[0].levelname == 'WARNING'
    assert 'Forbidden: /api/city/visited' in caplog.records[0].getMessage()
    assert response.status_code == 403


def auth_user_can_get_visited_cities__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_visited_cities'))

    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].getMessage() == (
        '(API) Successful request for a list of visited cities (user #1)   ' '/api/city/visited'
    )
    assert response.status_code == 200


def superuser_can_get_visited_cities__test(setup_db_without_visited_cities, client):
    client.login(username='superuser3', password='password')
    response = client.get(reverse('api__get_visited_cities'))

    assert response.status_code == 200


def auth_user_without_visited_cities_and_subscriptions_should_get_empty_list__test(
    setup_db_without_visited_cities, caplog, client
):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_visited_cities'))
    content = json.loads(response.content.decode())
    correct_content = []

    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].getMessage() == (
        '(API) Successful request for a list of visited cities (user #1)   ' '/api/city/visited'
    )
    assert content == correct_content


def auth_user_with_visited_cities_should_get_list_only_with_own_cities__test(
    setup_db_with_visited_cities, caplog, client
):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_visited_cities'))
    content = json.loads(response.content.decode())
    print(content)
    correct_content = [
        {
            'username': 'username1',
            'id': 3,
            'title': 'Город 3',
            'region_title': 'Регион 1 область',
            'region_id': 1,
            'lat': '1.0',
            'lon': '1.0',
            'year': 2024,
            'date_of_visit': '2024-12-30',
        },
        {
            'username': 'username1',
            'id': 2,
            'title': 'Город 2',
            'region_title': 'Регион 1 область',
            'region_id': 1,
            'lat': '1.0',
            'lon': '1.0',
            'year': 2024,
            'date_of_visit': '2024-12-30',
        },
        {
            'username': 'username1',
            'id': 1,
            'title': 'Город 1',
            'region_title': 'Регион 1 область',
            'region_id': 1,
            'lat': '1.0',
            'lon': '1.0',
            'year': 2024,
            'date_of_visit': '2024-12-30',
        },
    ]

    assert content == correct_content
