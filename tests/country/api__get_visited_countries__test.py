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
    create_visited_country,
    create_superuser,
)


@pytest.fixture
def setup_db(client, django_user_model):
    user1 = create_user(django_user_model, 1)
    user2 = create_user(django_user_model, 2)
    create_user(django_user_model, 3)
    create_superuser(django_user_model, 4)
    part_of_the_world = create_part_of_the_world(1)
    location = create_location(1, part_of_the_world[0])
    country = create_country(5, location[0])
    create_visited_country(country[0], user1)
    create_visited_country(country[1], user1)
    create_visited_country(country[0], user2)


def access_by_POST_is_prohibided__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.post(reverse('api__get_visited_countries'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/country/visited'
    assert response.status_code == 405
    assert response.json() == {'detail': 'Метод "POST" не разрешен.'}


def access_by_DELETE_is_prohibided__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.delete(reverse('api__get_visited_countries'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/country/visited'
    assert response.status_code == 405
    assert response.json() == {'detail': 'Метод "DELETE" не разрешен.'}


def access_by_PUT_is_prohibided__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.put(reverse('api__get_visited_countries'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/country/visited'
    assert response.status_code == 405
    assert response.json() == {'detail': 'Метод "PUT" не разрешен.'}


def access_by_PATCH_is_prohibided__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.patch(reverse('api__get_visited_countries'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/country/visited'
    assert response.status_code == 405
    assert response.json() == {'detail': 'Метод "PATCH" не разрешен.'}


def test_access_by_GET_without_auth_is_prohibided__test(setup_db, caplog, client):
    response = client.get(reverse('api__get_visited_countries'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Forbidden: /api/country/visited'
    assert response.status_code == 403
    assert response.json() == {'detail': 'Учетные данные не были предоставлены.'}


def access_by_GET_with_auth_is_allowed__user1__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_visited_countries'))
    expected_response = [{'code': '1', 'name': 'Страна 1'}, {'code': '2', 'name': 'Страна 2'}]

    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Country): Successful request for a list of visited countries '
        'from unknown location   /api/country/visited'
    )
    assert response.status_code == 200
    assert response.json() == expected_response


def test__access_by_GET_with_auth_is_allowed__user1__with_from_page__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_visited_countries') + '?from=country+map')
    expected_response = [{'code': '1', 'name': 'Страна 1'}, {'code': '2', 'name': 'Страна 2'}]

    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Country): Successful request for a list of visited countries '
        'from country map   /api/country/visited?from=country+map'
    )
    assert response.status_code == 200
    assert response.json() == expected_response


def access_by_GET_with_auth_is_allowed__user2__test(setup_db, caplog, client):
    client.login(username='username2', password='password')
    response = client.get(reverse('api__get_visited_countries'))
    expected_response = [{'code': '1', 'name': 'Страна 1'}]

    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Country): Successful request for a list of visited countries '
        'from unknown location   /api/country/visited'
    )
    assert response.status_code == 200
    assert response.json() == expected_response


def access_by_GET_with_auth_is_allowed__user2__with_from_page__test(setup_db, caplog, client):
    client.login(username='username2', password='password')
    response = client.get(reverse('api__get_visited_countries') + '?from=country+map')
    expected_response = [{'code': '1', 'name': 'Страна 1'}]

    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Country): Successful request for a list of visited countries '
        'from country map   /api/country/visited?from=country+map'
    )
    assert response.status_code == 200
    assert response.json() == expected_response


def access_by_GET_with_auth_is_allowed__user3__test(setup_db, caplog, client):
    client.login(username='username3', password='password')
    response = client.get(reverse('api__get_visited_countries'))
    expected_response = []

    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Country): Successful request for a list of visited countries '
        'from unknown location   /api/country/visited'
    )
    assert response.status_code == 200
    assert response.json() == expected_response


def access_by_GET_with_auth_is_allowed__user3__with_from_page__test(setup_db, caplog, client):
    client.login(username='username3', password='password')
    response = client.get(reverse('api__get_visited_countries') + '?from=country+map')
    expected_response = []

    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Country): Successful request for a list of visited countries '
        'from country map   /api/country/visited?from=country+map'
    )
    assert response.status_code == 200
    assert response.json() == expected_response
