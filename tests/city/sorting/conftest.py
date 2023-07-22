import pytest

from region.models import Area, Region
from city.models import City, VisitedCity


@pytest.fixture
def setup_db_for_sorting(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(id=1, area=area, title='Регион 1', type='область', iso3166='RU-RU')
    city_1 = City.objects.create(title='Город 1', region=region, coordinate_width=1, coordinate_longitude=1)
    city_2 = City.objects.create(title='Город 2', region=region, coordinate_width=1, coordinate_longitude=1)
    city_3 = City.objects.create(title='Город 3', region=region, coordinate_width=1, coordinate_longitude=1)
    city_4 = City.objects.create(title='Город 4', region=region, coordinate_width=1, coordinate_longitude=1)
    visited_city_1 = VisitedCity.objects.create(
        user=user, region=region, city=city_1, date_of_visit="2022-01-01", has_magnet=False, rating=3
    )
    visited_city_2 = VisitedCity.objects.create(
        user=user, region=region, city=city_2, has_magnet=False, rating=3
    )
    visited_city_3 = VisitedCity.objects.create(
        user=user, region=region, city=city_3, date_of_visit="2023-01-01", has_magnet=False, rating=3
    )

    return user
