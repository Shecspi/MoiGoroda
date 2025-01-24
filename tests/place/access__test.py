from django.test import Client
from django.urls import reverse

from tests.create_db import create_user


def test__unauthorized_user_does_not_have_access_to_the_page():
    client = Client()
    response = client.get('/place/map')

    assert response.status_code == 302

    response = client.get(reverse('place_map'), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


def test__authorized_user_have_access_to_the_page(django_user_model):
    create_user(django_user_model, 1)

    client = Client()

    client.login(username='username1', password='password')
    response = client.get(reverse('place_map'), follow=True)
    assert response.status_code == 200
