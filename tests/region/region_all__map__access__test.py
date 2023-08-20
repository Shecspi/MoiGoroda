"""
Тестирует доступность страницы для авторизованного и неавторизованного пользователей.
Страница тестирования '/region/all/map'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from django.urls import reverse


@pytest.fixture
def setup_db__access_region_all(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')


@pytest.mark.django_db
def test_access_guest(client):
    response = client.get(reverse('region-all-map'))

    assert response.status_code == 200
    assert 'region/region_all__map.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_access_auth_user(setup_db__access_region_all, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-all-map'))

    assert response.status_code == 200
    assert 'region/region_all__map.html' in (t.name for t in response.templates)
