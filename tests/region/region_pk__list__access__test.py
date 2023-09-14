"""
Тестирует доступность страницы для авторизованного и неавторизованного пользователей.
Страница тестирования '/region/<pk>'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from django.urls import reverse

from region.models import Region, Area


@pytest.fixture
def setup_db__access_region_pk(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    Region.objects.create(id=1, area=area, title='Регион 1', type='область', iso3166='RU-RU')


@pytest.mark.django_db
def test__access__auth_user(setup_db__access_region_pk, client):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected-list', kwargs={'pk': 1}))

    assert response.status_code == 200
    assert 'region/region_selected__list.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__access__guest(setup_db__access_region_pk, client):
    response = client.get(reverse('region-selected-list', kwargs={'pk': 1}))

    assert response.status_code == 200
    assert 'region/region_selected__list.html' in (t.name for t in response.templates)
