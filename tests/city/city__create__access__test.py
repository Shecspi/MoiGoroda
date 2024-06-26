"""
Тестирует доступность страницы для авторизованного и неавторизованного пользователей.
Страница тестирования '/city/create'.

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
def test__access__guest(client):
    response = client.get(reverse('city-create'))
    assert response.status_code == 302

    response = client.get(reverse('city-create'), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__access__auth_user(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-create'))

    assert response.status_code == 200
    assert 'city/city_create.html' in (t.name for t in response.templates)
