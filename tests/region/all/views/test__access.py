"""
Тестирует доступность страницы для авторизованного и неавторизованного пользователей.
Страница тестирования '/region/all'.

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
    """
    Тестирование того, что у неавторизованного пользователя есть доступ на страницу и отображается корректный шаблон.
    """
    response = client.get(reverse('region-all'))

    assert response.status_code == 200
    assert 'region/region__list.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_access_auth_user(setup_db, client):
    """
    Тестирование того, что у авторизованного пользователя есть доступ на страницу и отображается корректный шаблон.
    """
    client.login(username='username', password='password')
    response = client.get(reverse('region-all'))

    assert response.status_code == 200
    assert 'region/region__list.html' in (t.name for t in response.templates)
