from datetime import datetime

from django.contrib.auth.models import User

from city.models import City, VisitedCity
from region.models import Area, Region


def create_user(django_user_model, user_id: int):
    return django_user_model.objects.create_user(
        id=user_id, username=f'username{user_id}', password='password'
    )


def create_area(num: int) -> list[Area]:
    return [Area.objects.create(id=1, title=f'Округ {i}') for i in range(1, num + 1)]


def create_region(num: int, area: Area) -> list[Region]:
    return [
        Region.objects.create(
            id=1, area=area, title=f'Регион {i}', type='область', iso3166=f'RU-RU{i}'
        )
        for i in range(1, num + 1)
    ]


def create_city(num: int, region: Region) -> list[City]:
    return [
        City.objects.create(
            id=i, title=f'Город {i}', region=region, coordinate_width=1, coordinate_longitude=1
        )
        for i in range(1, num + 1)
    ]


def create_visited_city(
    region: Region, user: User, city: City, date_of_visit: datetime, has_magnet: bool, rating: int
) -> VisitedCity:
    return VisitedCity.objects.create(
        user=user,
        region=region,
        city=city,
        date_of_visit=date_of_visit,
        has_magnet=has_magnet,
        rating=rating,
    )
