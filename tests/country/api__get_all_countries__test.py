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
    create_country(5, location[0])


@pytest.fixture
def setup_empty_db(client, django_user_model):
    create_user(django_user_model, 1)
    part_of_the_world = create_part_of_the_world(1)
    location = create_location(1, part_of_the_world[0])


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


def access_by_GET_without_auth_is_allowed__test(setup_db, caplog, client):
    response = client.get(reverse('api__get_all_countries'))
    expected_response = [
        {
            'id': 1,
            'to_delete': '/api/country/delete/1',
            'name': 'Страна 1',
            'fullname': 'Полное имя страны 1',
            'code': '1',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 2,
            'to_delete': '/api/country/delete/2',
            'name': 'Страна 2',
            'fullname': 'Полное имя страны 2',
            'code': '2',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 3,
            'to_delete': '/api/country/delete/3',
            'name': 'Страна 3',
            'fullname': 'Полное имя страны 3',
            'code': '3',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 4,
            'to_delete': '/api/country/delete/4',
            'name': 'Страна 4',
            'fullname': 'Полное имя страны 4',
            'code': '4',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 5,
            'to_delete': '/api/country/delete/5',
            'name': 'Страна 5',
            'fullname': 'Полное имя страны 5',
            'code': '5',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
    ]

    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Country): Successful request for a list of all countries from unknown location   /api/country/all'
    )
    assert response.status_code == 200
    assert response.json() == expected_response


def access_by_GET_with_auth_is_allowed__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_all_countries'))
    expected_response = [
        {
            'id': 1,
            'to_delete': '/api/country/delete/1',
            'name': 'Страна 1',
            'fullname': 'Полное имя страны 1',
            'code': '1',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 2,
            'to_delete': '/api/country/delete/2',
            'name': 'Страна 2',
            'fullname': 'Полное имя страны 2',
            'code': '2',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 3,
            'to_delete': '/api/country/delete/3',
            'name': 'Страна 3',
            'fullname': 'Полное имя страны 3',
            'code': '3',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 4,
            'to_delete': '/api/country/delete/4',
            'name': 'Страна 4',
            'fullname': 'Полное имя страны 4',
            'code': '4',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 5,
            'to_delete': '/api/country/delete/5',
            'name': 'Страна 5',
            'fullname': 'Полное имя страны 5',
            'code': '5',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
    ]

    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Country): Successful request for a list of all countries from unknown location   /api/country/all'
    )
    assert response.status_code == 200
    assert response.json() == expected_response


def access_by_GET_with_auth_is_allowed__with_from_page__test(setup_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_all_countries') + '?from=country+map')
    expected_response = [
        {
            'id': 1,
            'to_delete': '/api/country/delete/1',
            'name': 'Страна 1',
            'fullname': 'Полное имя страны 1',
            'code': '1',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 2,
            'to_delete': '/api/country/delete/2',
            'name': 'Страна 2',
            'fullname': 'Полное имя страны 2',
            'code': '2',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 3,
            'to_delete': '/api/country/delete/3',
            'name': 'Страна 3',
            'fullname': 'Полное имя страны 3',
            'code': '3',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 4,
            'to_delete': '/api/country/delete/4',
            'name': 'Страна 4',
            'fullname': 'Полное имя страны 4',
            'code': '4',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
        {
            'id': 5,
            'to_delete': '/api/country/delete/5',
            'name': 'Страна 5',
            'fullname': 'Полное имя страны 5',
            'code': '5',
            'location': 'Локация 1',
            'part_of_the_world': 'Часть света 1',
            'is_member_of_un': False,
        },
    ]

    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Country): Successful request for a list of all countries '
        'from country map   /api/country/all?from=country+map'
    )
    assert response.status_code == 200
    assert response.json() == expected_response


def access_by_GET_without_auth_is_allowed__without_countries__test(setup_empty_db, caplog, client):
    response = client.get(reverse('api__get_all_countries'))
    expected_response = []
    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Country): Successful request for a list of all countries from unknown location   /api/country/all'
    )
    assert response.status_code == 200
    assert response.json() == expected_response


def access_by_GET_with_auth_is_allowed__without_countries__test(setup_empty_db, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_all_countries'))
    expected_response = []
    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Country): Successful request for a list of all countries from unknown location   /api/country/all'
    )
    assert response.status_code == 200
    assert response.json() == expected_response
