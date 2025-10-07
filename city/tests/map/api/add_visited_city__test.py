"""

Copyright Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import json
from typing import Any

import pytest

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

from services.db.visited_city_repo import get_number_of_visited_cities
from test_data.add_visited_city import add_visited_city_test_data
from tests.create_db import (
    create_user,
    create_area,
    create_region,
    create_city,
)


@pytest.fixture
def setup_db_without_visited_cities(client: Client, django_user_model: Any) -> None:
    create_user(django_user_model, 1)
    area = create_area(1)
    region = create_region(1, area[0])
    create_city(4, region[0])


@pytest.mark.django_db
def access_by_GET_is_prohibited__test(
    setup_db_without_visited_cities: None, caplog: Any, client: Client
) -> None:
    client.login(username='username1', password='password')
    response = client.get(reverse('api__add_visited_city'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/add'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_DELETE_is_prohibited__test(
    setup_db_without_visited_cities: None, caplog: Any, client: Client
) -> None:
    client.login(username='username1', password='password')
    response = client.delete(reverse('api__add_visited_city'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/add'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_PUT_is_prohibited__test(
    setup_db_without_visited_cities: None, caplog: Any, client: Client
) -> None:
    client.login(username='username1', password='password')
    response = client.put(reverse('api__add_visited_city'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/add'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_PATCH_is_prohibited__test(
    setup_db_without_visited_cities: None, caplog: Any, client: Client
) -> None:
    client.login(username='username1', password='password')
    response = client.patch(reverse('api__add_visited_city'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/add'
    assert response.status_code == 405


@pytest.mark.django_db
def access_by_POST_for_guest_is_prohibited__test(
    setup_db_without_visited_cities: None, caplog: Any, client: Client
) -> None:
    response = client.get(reverse('api__add_visited_city'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Forbidden: /api/city/visited/add'
    assert response.status_code == 403


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize(
    'request_data, status_code, correct_response_data, log_level, log_message',
    add_visited_city_test_data,
)
def request_fields_and_response__test(
    setup_db_without_visited_cities: None,
    caplog: Any,
    client: Client,
    request_data: dict[str, Any],
    status_code: int,
    correct_response_data: dict[str, Any] | bool,
    log_level: str | bool,
    log_message: str | bool,
) -> None:
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


def db_after_succesful_request__test(
    setup_db_without_visited_cities: None, caplog: Any, client: Client
) -> None:
    num_before = get_number_of_visited_cities(1)
    client.login(username='username1', password='password')
    client.post(
        reverse('api__add_visited_city'),
        data=json.dumps(
            {
                'city': 1,
                'date_of_visit': '2024-08-01',
                'has_magnet': True,
                'impression': 'impression',
                'rating': 3,
            }
        ),
        content_type='application/json',
    )
    num_after = get_number_of_visited_cities(1)

    assert num_after == num_before + 1


def db_after_unsuccesful_request__test(
    setup_db_without_visited_cities: None, caplog: Any, client: Client
) -> None:
    num_before = get_number_of_visited_cities(1)
    client.login(username='username1', password='password')
    client.post(
        reverse('api__add_visited_city'),
        data=json.dumps({}),
        content_type='application/json',
    )
    num_after = get_number_of_visited_cities(1)

    assert num_after == num_before
