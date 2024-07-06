import pytest
from django.contrib.auth.models import User

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
        id=1, title='Город 1', region=region, coordinate_width=1, coordinate_longitude=1
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
    create_user(django_user_model, 2)
    area = create_area()
    region = create_region(area)
    city = create_city(region)
    create_visited_city(user1, region, city)
