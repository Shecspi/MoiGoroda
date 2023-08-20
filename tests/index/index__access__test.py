"""
Тестирует доступность страницы для пользователей.
Страница тестирования '/'.

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
    response = client.get(reverse('main_page'))

    assert response.status_code == 200
    assert 'index.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_access_auth_user(client):
    client.login(username='username', password='password')
    response = client.get(reverse('main_page'))

    assert response.status_code == 200
    assert 'index.html' in (t.name for t in response.templates)
