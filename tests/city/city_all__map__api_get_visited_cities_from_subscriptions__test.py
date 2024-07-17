"""
----------------------------------------------

Copyright Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

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
    create_share_settings,
    create_subscription,
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


def test__access_by_POST_is_prohibited(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.post(reverse('api__get_visited_cities_from_subscriptions'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/subscriptions'
    assert response.status_code == 405


def test__access_by_DELETE_is_prohibited(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.delete(reverse('api__get_visited_cities_from_subscriptions'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/subscriptions'
    assert response.status_code == 405


def test__access_by_PUT_is_prohibited(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.put(reverse('api__get_visited_cities_from_subscriptions'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/subscriptions'
    assert response.status_code == 405


def test__access_by_PATCH_is_prohibited(setup_db_without_visited_cities, caplog, client):
    client.login(username='username1', password='password')
    response = client.patch(reverse('api__get_visited_cities_from_subscriptions'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == 'Method Not Allowed: /api/city/visited/subscriptions'
    assert response.status_code == 405


def guest_can_not_get_visited_cities__test(setup_db_without_visited_cities, caplog, client):
    response = client.get(reverse('api__get_visited_cities_from_subscriptions'))

    assert caplog.records[0].levelname == 'WARNING'
    assert 'Forbidden: /api/city/visited' in caplog.records[0].getMessage()
    assert response.status_code == 403


def user_without_correct_account_data_can_not_get_visited_cities__test(
    setup_db_without_visited_cities, caplog, client
):
    response = client.get(reverse('api__get_visited_cities_from_subscriptions'))
    client.login(username='username1111', password='password')

    assert caplog.records[0].levelname == 'WARNING'
    assert 'Forbidden: /api/city/visited' in caplog.records[0].getMessage()
    assert response.status_code == 403


@pytest.mark.django_db
def auth_user_can_get_visited_cities__test(setup_db_without_visited_cities, caplog, client):
    create_share_settings(2)
    create_subscription(1, 2)

    client.login(username='username1', password='password')
    response = client.get(
        reverse('api__get_visited_cities_from_subscriptions') + '?data={"ids":[2]}'
    )

    assert caplog.records[0].levelname == 'INFO'
    assert (
        '(API) Successful request for a list of visited cities from subscriptions (user #1)'
        in caplog.records[0].getMessage()
    )
    assert response.status_code == 200


@pytest.mark.django_db
def superuser_can_get_visited_cities__test(setup_db_without_visited_cities, caplog, client):
    create_share_settings(2)
    create_subscription(1, 2)

    client.login(username='superuser3', password='password')
    response = client.get(
        reverse('api__get_visited_cities_from_subscriptions') + '?data={"ids":[2]}'
    )

    assert caplog.records[0].levelname == 'INFO'
    assert (
        '(API) Successful request from superuser for a list of visited cities from subscriptions (user #3)'
        in caplog.records[0].getMessage()
    )
    assert response.status_code == 200


@pytest.mark.django_db
def superuser_can_get_visited_cities_without_permission__test(
    setup_db_without_visited_cities, caplog, client
):
    create_share_settings(2, can_subscribe=False)

    client.login(username='superuser3', password='password')
    response = client.get(
        reverse('api__get_visited_cities_from_subscriptions') + '?data={"ids":[2]}'
    )

    assert caplog.records[0].levelname == 'INFO'
    assert (
        '(API) Successful request from superuser for a list of visited cities from subscriptions (user #3)'
        in caplog.records[0].getMessage()
    )
    assert response.status_code == 200


def test_response_without_user_ids_can_not_be_performed__test(
    setup_db_without_visited_cities, caplog, client
):
    client.login(username='username1', password='password')
    response = client.get(reverse('api__get_visited_cities_from_subscriptions'))

    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].getMessage() == (
        '(API) An incorrect list of user IDs was received   ' '/api/city/visited/subscriptions'
    )
    assert response.status_code == 400
