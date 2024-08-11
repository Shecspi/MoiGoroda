"""

Copyright Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import json

import pytest

from django.urls import reverse

from test_data.add_visited_city import add_visited_city_test_data
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
    'request_data, status_code, correct_response_data, log_level, log_message',
    add_visited_city_test_data,
)
def request_fields_and_response__test(
    setup_db_without_visited_cities,
    caplog,
    client,
    request_data: dict,
    status_code: int,
    correct_response_data: dict | bool,
    log_level: str | bool,
    log_message: str | bool,
):
    client.login(username='username1', password='password')
    response = client.post(
        reverse('api__add_visited_city'),
        data=json.dumps(request_data),
        content_type='application/json',
    )
    response_data = json.loads(response.content.decode())

    assert response.status_code == status_code
    if correct_response_data:
        assert response_data == correct_response_data
    if log_level:
        assert caplog.records[0].levelname == log_level
    if log_message:
        assert caplog.records[0].getMessage() == log_message
