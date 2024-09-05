"""
----------------------------------------------

Copyright Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from django.urls import reverse

from tests.create_db import (
    create_user,
    create_part_of_the_world,
    create_location,
    create_country,
    create_superuser,
)


@pytest.fixture
def setup_db(client, django_user_model):
    create_user(django_user_model, 1)
    create_user(django_user_model, 2)
    create_superuser(django_user_model, 3)
    part_of_the_world = create_part_of_the_world(1)
    location = create_location(1, part_of_the_world[0])
    country = create_country(5, location[0])


def access_by_POST_is_prohibided__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.post(reverse('api__get_all_countries'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/country/all'
    assert response.status_code == 405
    assert response.json() == {'detail': 'Метод "POST" не разрешен.'}


def access_by_DELETE_is_prohibided__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.delete(reverse('api__get_all_countries'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/country/all'
    assert response.status_code == 405
    assert response.json() == {'detail': 'Метод "DELETE" не разрешен.'}


def access_by_PUT_is_prohibided__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.put(reverse('api__get_all_countries'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/country/all'
    assert response.status_code == 405
    assert response.json() == {'detail': 'Метод "PUT" не разрешен.'}


def access_by_PATCH_is_prohibided__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.patch(reverse('api__get_all_countries'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/country/all'
    assert response.status_code == 405
    assert response.json() == {'detail': 'Метод "PATCH" не разрешен.'}
