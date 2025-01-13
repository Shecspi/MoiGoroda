from datetime import datetime

from django.contrib.auth.models import User

from account.models import ShareSettings
from city.models import City, VisitedCity
from country.models import Country, Location, PartOfTheWorld, VisitedCountry
from news.models import News
from place.models import Category, Place
from region.models import Area, Region
from subscribe.models import Subscribe


def create_user(django_user_model, user_id: int):
    return django_user_model.objects.create_user(
        id=user_id, username=f'username{user_id}', password='password'
    )


def create_superuser(django_user_model, user_id: int):
    return django_user_model.objects.create_superuser(
        id=user_id, username=f'superuser{user_id}', password='password'
    )


def create_part_of_the_world(num: int) -> list[PartOfTheWorld]:
    return [PartOfTheWorld.objects.create(id=i, name=f'Часть света {i}') for i in range(1, num + 1)]


def create_location(num: int, part_of_the_world: PartOfTheWorld) -> list[Location]:
    return [
        Location.objects.create(
            id=i,
            name=f'Локация {i}',
            part_of_the_world=part_of_the_world,
        )
        for i in range(1, num + 1)
    ]


def create_country(num: int, location: Location) -> list[Country]:
    return [
        Country.objects.create(
            id=i,
            name=f'Страна {i}',
            fullname=f'Полное имя страны {i}',
            code=f'{i}',
            location=location,
        )
        for i in range(1, num + 1)
    ]


def create_visited_country(country: Country, user: User) -> VisitedCountry:
    return VisitedCountry.objects.create(country=country, user=user)


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


def create_news(id: int, title: str, content: str) -> News:
    return News.objects.create(id=id, title=title, content=content)


def create_share_settings(
    user_id: int,
    can_share: bool = True,
    can_share_dashboard: bool = True,
    can_share_city_map: bool = True,
    can_share_region_map: bool = True,
    can_subscribe: bool = True,
) -> ShareSettings:
    return ShareSettings.objects.create(
        user_id=user_id,
        can_share=can_share,
        can_share_dashboard=can_share_dashboard,
        can_share_city_map=can_share_city_map,
        can_share_region_map=can_share_region_map,
        can_subscribe=can_subscribe,
    )


def create_subscription(subscribe_from_id: int, subscribe_to_id: int) -> Subscribe:
    return Subscribe.objects.create(
        subscribe_from_id=subscribe_from_id, subscribe_to_id=subscribe_to_id
    )


def create_category_of_place(id: int = 1) -> Category:
    return Category.objects.create(id=id, name=f'Тип места {id}')


def create_place(name: str, lat: float, lon: float, category: Category, user: User) -> Place:
    return Place.objects.create(
        name=name, latitude=lat, longitude=lon, category=category, user=user
    )
