from django.urls import reverse, NoReverseMatch

from tests.create_db import create_user


def test__url_path_to_create_place_exists():
    try:
        reverse('create_place')
    except NoReverseMatch:
        assert False
    else:
        assert True


def test__access_by_GET_is_prohibited(client, django_user_model):
    create_user(django_user_model, 1)
    client.login(username='username1', password='password')
    response = client.post(reverse('create_place'))

    assert response.status_code == 405


def test__access_by_POST_is_allowed(client, django_user_model):
    create_user(django_user_model, 1)
    client.login(username='username1', password='password')
    response = client.post(reverse('create_place'))

    assert response.status_code == 200


def test__access_by_PUT_is_prohibited(client, django_user_model):
    create_user(django_user_model, 1)
    client.login(username='username1', password='password')
    response = client.put(reverse('create_place'))

    assert response.status_code == 405


def test__access_by_PATCH_is_prohibited(client, django_user_model):
    create_user(django_user_model, 1)
    client.login(username='username1', password='password')
    response = client.patch(reverse('create_place'))

    assert response.status_code == 405


def test__access_by_DELETE_is_prohibited(client, django_user_model):
    create_user(django_user_model, 1)
    client.login(username='username1', password='password')
    response = client.delete(reverse('create_place'))

    assert response.status_code == 405


def test__api_for_creation_place_return_403_for_not_auth_user(client):
    response = client.get(reverse('create_place'))

    assert response.status_code == 403
