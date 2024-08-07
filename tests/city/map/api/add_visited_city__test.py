"""

Copyright Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

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
