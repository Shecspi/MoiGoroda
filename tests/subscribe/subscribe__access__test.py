import json
import pytest

from django.urls import reverse

from tests.subscribe.conftest import create_permissions_in_db


@pytest.mark.django_db
def auth_user_has_permission_to_change_own_subscriptions__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, True))

    client.login(username='username2', password='password')
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': 2, 'to_id': 1, 'action': 'subscribe'}),
        content_type='application/json',
    )

    assert response.status_code == 200


@pytest.mark.django_db
def auth_user_has_no_permission_to_change_other_people_subscriptions__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, True))

    client.login(username='username2', password='password')
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': 1, 'to_id': 3, 'action': 'subscribe'}),
        content_type='application/json',
    )

    assert response.status_code == 403


@pytest.mark.django_db
def user_is_allowed_to_subscribe_to_himself__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, True))

    client.login(username='username2', password='password')
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': 2, 'to_id': 1, 'action': 'subscribe'}),
        content_type='application/json',
    )

    assert response.status_code == 200


@pytest.mark.django_db
def user_is_not_allowed_to_subscribe_to_himself__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, False))

    client.login(username='username2', password='password')
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': 2, 'to_id': 1, 'action': 'subscribe'}),
        content_type='application/json',
    )

    assert response.status_code == 403


@pytest.mark.django_db
def incorrect_json_fromid_data__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, True))

    client.login(username='username2', password='password')
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': 'a', 'to_id': 1, 'action': 'subscribe'}),
        content_type='application/json',
    )

    assert response.status_code == 400


@pytest.mark.django_db
def incorrect_json_toid_data__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, True))

    client.login(username='username2', password='password')
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': 2, 'to_id': 'e', 'action': 'subscribe'}),
        content_type='application/json',
    )

    assert response.status_code == 400


@pytest.mark.django_db
def incorrect_json_action_data__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, True))

    client.login(username='username2', password='password')
    response = client.post(
        reverse('save_subscribe'),
        data=json.dumps({'from_id': 2, 'to_id': 1, 'action': 'casdsa'}),
        content_type='application/json',
    )

    assert response.status_code == 400
