"""

Copyright Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

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
    create_superuser(django_user_model, 2)
    area = create_area(1)
    region = create_region(1, area[0])
    create_city(4, region[0])


@pytest.fixture
def setup_db_with_1_visited_city(client, django_user_model):
    user1 = create_user(django_user_model, 1)
    area = create_area(1)
    region = create_region(1, area[0])
    city = create_city(4, region[0])
    create_visited_city(
        region=region[0],
        user=user1,
        city=city[0],
        date_of_visit=datetime.now(),
        has_magnet=True,
        rating=5,
    )


@pytest.fixture
def setup_db_with_4_visited_city(client, django_user_model):
    user1 = create_user(django_user_model, 1)
    area = create_area(1)
    region = create_region(1, area[0])
    city = create_city(4, region[0])
    for i in range(4):
        create_visited_city(
            region=region[0],
            user=user1,
            city=city[i],
            date_of_visit=datetime.now(),
            has_magnet=True,
            rating=5,
        )


@pytest.mark.django_db
def access_by_POST_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.post(reverse('api__get_not_visited_cities'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/not_visited'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_DELETE_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.delete(reverse('api__get_not_visited_cities'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/not_visited'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_PUT_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.put(reverse('api__get_not_visited_cities'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/not_visited'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_PATCH_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.patch(reverse('api__get_not_visited_cities'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/not_visited'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_GET_for_auth_user_is_allowed__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_not_visited_cities'))

    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].getMessage() == (
        '(API) Successful request for a list of not visited cities (user #1)   '
        '/api/city/not_visited'
    )
    assert response.status_code == 200


@pytest.mark.django_db
def access_by_GET_for_superuser_is_allowed__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='superuser2', password='password')
    response = client.get(reverse('api__get_not_visited_cities'))

    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].getMessage() == (
        '(API) Successful request for a list of not visited cities (user #2)   '
        '/api/city/not_visited'
    )
    assert response.status_code == 200


@pytest.mark.django_db
def access_by_GET_for_guest_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    response = client.get(reverse('api__get_not_visited_cities'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Forbidden: /api/city/not_visited'
    assert response.status_code == 403


@pytest.mark.django_db
def response_with_0_visited_cities__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_not_visited_cities'))
    content = json.loads(response.content.decode())
    correct_response = [
        {'id': 1, 'title': 'Город 1', 'lat': '1.0', 'lon': '1.0'},
        {'id': 2, 'title': 'Город 2', 'lat': '1.0', 'lon': '1.0'},
        {'id': 3, 'title': 'Город 3', 'lat': '1.0', 'lon': '1.0'},
        {'id': 4, 'title': 'Город 4', 'lat': '1.0', 'lon': '1.0'},
    ]

    assert content == correct_response
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].getMessage() == (
        '(API) Successful request for a list of not visited cities (user #1)   '
        '/api/city/not_visited'
    )


@pytest.mark.django_db
def response_with_1_visited_city__test(setup_db_with_1_visited_city, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_not_visited_cities'))
    content = json.loads(response.content.decode())
    correct_response = [
        {'id': 2, 'title': 'Город 2', 'lat': '1.0', 'lon': '1.0'},
        {'id': 3, 'title': 'Город 3', 'lat': '1.0', 'lon': '1.0'},
        {'id': 4, 'title': 'Город 4', 'lat': '1.0', 'lon': '1.0'},
    ]

    assert content == correct_response
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].getMessage() == (
        '(API) Successful request for a list of not visited cities (user #1)   '
        '/api/city/not_visited'
    )


@pytest.mark.django_db
def response_with_4_visited_city__test(setup_db_with_4_visited_city, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_not_visited_cities'))
    content = json.loads(response.content.decode())
    correct_response = []

    assert content == correct_response
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].getMessage() == (
        '(API) Successful request for a list of not visited cities (user #1)   '
        '/api/city/not_visited'
    )
