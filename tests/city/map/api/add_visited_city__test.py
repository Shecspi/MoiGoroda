"""

Copyright Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import json

import pytest

from django.urls import reverse

from tests.create_db import (
    create_user,
    create_area,
    create_region,
    create_city,
)


@pytest.fixture
def setup_db_without_visited_cities(client, django_user_model):
    create_user(django_user_model, 1)
    area = create_area(1)
    region = create_region(1, area[0])
    create_city(4, region[0])


@pytest.mark.django_db
def access_by_GET_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__add_visited_city'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/add'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_DELETE_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.delete(reverse('api__add_visited_city'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/add'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_PUT_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.put(reverse('api__add_visited_city'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/add'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_PATCH_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.patch(reverse('api__add_visited_city'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/add'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_POST_for_guest_is_prohibited__test(setup_db_without_visited_cities, caplog, client):
    response = client.get(reverse('api__add_visited_city'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Forbidden: /api/city/visited/add'
    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    'request_data, correct_response_data, log_message',
    (
        (
            {
                'city': 1,
                'date_of_visit': '2024-08-01',
                'has_magnet': True,
                'impression': 'impression',
                'rating': 3,
            },
            {
                'status': 'success',
                'city': {
                    'id': 1,
                    'city': 1,
                    'city_title': 'Город 1',
                    'region_title': 'Регион 1 область',
                    'date_of_visit': '2024-08-01',
                    'has_magnet': True,
                    'impression': 'impression',
                    'rating': 3,
                },
            },
            '(API: Add visited city) The visited city has been successfully added from unknown location   /api/city/visited/add',
        ),
    ),
)
def test__response_with_correct_request_data(
    setup_db_without_visited_cities,
    caplog,
    client,
    request_data,
    correct_response_data,
    log_message,
):
    client.login(username='username1', password='password')
    response = client.post(
        reverse('api__add_visited_city'),
        data=json.dumps(request_data),
        content_type='application/json',
    )
    response_data = json.loads(response.content.decode())
    assert response_data == correct_response_data
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].getMessage() == log_message
