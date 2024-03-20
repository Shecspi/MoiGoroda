import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from city.models import City, VisitedCity
from region.models import Area, Region


def create_user(django_user_model, user_id: int):
    return django_user_model.objects.create_user(
        id=user_id, username=f'username{user_id}', password='password'
    )


def create_area():
    return Area.objects.create(title='Округ 1')


def create_region(area: Area):
    return Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')


def create_city(region: Region):
    """
    Добавляет в базу данных города и возвращает список с инстансами созданных городов.
    """
    return City.objects.create(
        id=1, title=f'Город 1', region=region, coordinate_width=1, coordinate_longitude=1
    )


def create_visited_city(user: User, region: Region, city: City):
    return VisitedCity.objects.create(
        id=1,
        user=user,
        region=region,
        city=city,
        date_of_visit='2022-02-02',
        has_magnet=False,
        rating=3,
    )


@pytest.fixture
def setup(client, django_user_model):
    user1 = create_user(django_user_model, 1)
    user2 = create_user(django_user_model, 2)
    area = create_area()
    region = create_region(area)
    city = create_city(region)
    visited_city = create_visited_city(user1, region, city)


@pytest.mark.django_db
def test__access__get__auth_user(setup, client):
    """
    Доступ через GET авторизованным пользователям запрещён. Перенаправление на форму авторизации.
    """
    client.login(username='username1', password='password')
    response = client.get(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 403


@pytest.mark.django_db
def test__access__get__guest(setup, client):
    """
    Доступ через GET неавторизованным пользователям запрещён. Перенаправление на форму авторизации.
    """
    response = client.get(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 302

    response = client.get(reverse('city-delete', kwargs={'pk': 1}), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__access__post__auth_user(setup, client):
    """
    Успешное удаление существующего города и перенаправление в результате в список городов.
    """
    client.login(username='username1', password='password')
    response = client.post(reverse('city-delete', kwargs={'pk': 1}), follow=True)
    assert response.status_code == 200
    assert 'city/city_all__list.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__access__post__guest(setup, client):
    """
    При попытке удалить существующий город с неавторизованной учтной записи
    происходит перенаправление на форму авторизации.
    """
    response = client.post(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 302

    response = client.post(reverse('city-delete', kwargs={'pk': 1}), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__access__post__auth_user__not_owner(setup, client):
    """
    При попытке удалить город, который не принадлежит пользователю, возвращается ошибка 404.
    """
    client.login(username='username2', password='password')
    response = client.post(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 404
