"""
Тестирует доступность страницы для авторизованного и неавторизованного пользователей.
Страница тестирования '/city/delete/<pk>'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from city.models import City, VisitedCity
from region.models import Area, Region


@pytest.fixture
def setup_db(client, django_user_model):
    user_1 = django_user_model.objects.create_user(username='username1', password='password')
    user_2 = django_user_model.objects.create_user(username='username2', password='password')
    area = Area.objects.create(title='Area 1')
    region = Region.objects.create(area=area, title='Регион 1', type='O')
    city = City.objects.create(title='Город 1', region=region, coordinate_width=1, coordinate_longitude=1)
    visited_city_1 = VisitedCity.objects.create(id=1, user=user_1, region=region, city=city, rating='5')
    visited_city_2 = VisitedCity.objects.create(id=2, user=user_2, region=region, city=city, rating='5')


@pytest.mark.django_db
def test__access__guest_by_get(setup_db, client):
    response = client.get(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 302

    response = client.get(reverse('city-delete', kwargs={'pk': 1}), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__access__guest_by_post(setup_db, client):
    response = client.post(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 302

    response = client.get(reverse('city-delete', kwargs={'pk': 1}), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__access__auth_user_by_get(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 403


@pytest.mark.django_db
def test__access__incorrect_user_by_get(setup_db, client):
    client.login(username='username2', password='password')
    response = client.get(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 403


@pytest.mark.django_db
def test__access__incorrect_user_by_post(setup_db, client):
    client.login(username='username2', password='password')
    response = client.post(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 404


@pytest.mark.django_db
def test__access__auth_user_by_post_1(setup_db, client):
    client.login(username='username1', password='password')
    user = User.objects.get(username='username1')
    qty_before = VisitedCity.objects.filter(user=user).count()
    response = client.post(reverse('city-delete', kwargs={'pk': 1}))
    qty_after = VisitedCity.objects.filter(user=user).count()
    assert qty_before - qty_after == 1
    assert response.status_code == 302


@pytest.mark.django_db
def test__access__auth_user_by_post_2(setup_db, client):
    client.login(username='username1', password='password')
    user = User.objects.get(username='username1')
    qty_before = VisitedCity.objects.filter(user=user).count()
    response = client.post(reverse('city-delete', kwargs={'pk': 1}), follow=True)
    qty_after = VisitedCity.objects.filter(user=user).count()
    assert qty_before - qty_after == 1
    assert response.status_code == 200
    assert 'city/city_all__list.html' in (t.name for t in response.templates)
