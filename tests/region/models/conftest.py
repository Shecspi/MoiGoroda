import pytest

from region.models import Area, Region
from city.models import City, VisitedCity

from django.db import transaction


@pytest.fixture
def create_user(client, django_user_model):
    new_user = django_user_model.objects.create_user(
        username='username', password='password'
    )
    return new_user


@pytest.fixture
def setup_db():
    areas = [
        'Южный федеральный округ',
        'Дальневосточный федеральный округ',
        'Северо-Кавказский федеральный округ'
    ]
    regions = [
        [1, 'Адыгея', 'R', 'RU-AD'],
        [1, 'Краснодарский', 'K', 'RU-KDA'],
        [1, 'Волгоградская', 'O', 'RU-VGG'],
        [1, 'Севастополь', 'G', 'RU-SEV'],
        [2, 'Еврейская', 'AOb', 'RU-YEV'],
        [2, 'Чукотский', 'AOk', 'RU-CHU'],
        [3, 'Чеченская республика', 'R', 'RU-CE']
    ]
    with transaction.atomic():
        for area in areas:
            area = Area.objects.create(
                title=area
            )
            for region in regions:
                if region[0] == area.id:
                    Region.objects.create(
                        area=area,
                        title=region[1],
                        type=region[2],
                        iso3166=region[3]
                    )


@pytest.fixture
def setup_db_for_sorting(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU')
    city_1 = City.objects.create(title='Город 1', region=region, coordinate_width=1, coordinate_longitude=1)
    city_2 = City.objects.create(title='Город 2', region=region, coordinate_width=1, coordinate_longitude=1)
    city_3 = City.objects.create(title='Город 3', region=region, coordinate_width=1, coordinate_longitude=1)
    visited_city_1 = VisitedCity.objects.create(
        user=user, region=region, city=city_1, date_of_visit="2022-01-01", has_magnet=False, rating=3
    )
    visited_city_2 = VisitedCity.objects.create(
        user=user, region=region, city=city_2, has_magnet=False, rating=3
    )
    visited_city_3 = VisitedCity.objects.create(
        user=user, region=region, city=city_3, date_of_visit="2023-01-01", has_magnet=False, rating=3
    )
