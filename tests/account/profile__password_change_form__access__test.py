"""
Тестирует доступность страницы для авторизованного пользователя.
Страница тестирования '/account/password/change/'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from django.urls import reverse


@pytest.fixture
def setup_db(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')


@pytest.mark.django_db
def test_access_guest(client):
    response = client.get(reverse('password_change_form'))
    assert response.status_code == 302

    response = client.get(reverse('password_change_form'), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_access_auth_user(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('password_change_form'))

    assert response.status_code == 200
    assert 'account/profile__password_change_form.html' in (t.name for t in response.templates)
