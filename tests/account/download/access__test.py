import pytest
from django.urls import reverse

from tests.account.download.create_db import create_user


@pytest.mark.django_db
def test__access_by_get_for_guest_is_prohibited(client):
    response = client.get(reverse('download'))
    assert response.status_code == 405


@pytest.mark.django_db
def test__access_by_get_for_auth_user_is_prohibited(django_user_model, client):
    create_user(django_user_model, 1)

    client.login(username='username1', password='password')
    response = client.get(reverse('download'))

    assert response.status_code == 405


@pytest.mark.django_db
def test__access_by_post_for_guest_is_prohibited(client):
    response = client.post(reverse('download'))
    assert response.status_code == 302

    response = client.post(reverse('download'), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__access_by_post_for_auth_user_is_allowed(django_user_model, client):
    create_user(django_user_model, 1)

    client.login(username='username1', password='password')
    data = {'reporttype': 'city', 'filetype': 'txt'}
    response = client.post(reverse('download'), data=data)

    assert response.status_code == 200
    assert response.content.decode() == (
        'Город     Регион     Дата посещения     ' 'Наличие сувенира     Оценка     \n'
    )
