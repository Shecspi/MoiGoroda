import pytest
from django.contrib.auth.models import User

from django.db import transaction

from region.models import Area, Region
from city.models import City, VisitedCity


@pytest.fixture
def create_user(client, django_user_model):
    new_user = django_user_model.objects.create_user(
        username='username', password='password'
    )
    return new_user


@pytest.fixture
def setup_db():
    area = Area.objects.create(title='Area 1')
    with transaction.atomic():
        for number in range(1, 21):
            Region.objects.create(
                area=area,
                title=f'Регион {number}',
                type='O',
                iso3166=f'RU-{number}'
            )
        for number in range(1, 21):
            City.objects.create(
                title=f'Город {number}',
                region=Region.objects.get(id=number),
                coordinate_width=55.55,
                coordinate_longitude=66.66
            )


@pytest.fixture
def setup_visited_cities_10_cities():
    for number in range(1, 11):
        VisitedCity.objects.create(
            user=User.objects.get(id=1),
            region=Region.objects.get(id=number),
            city=City.objects.get(id=number),
            has_magnet=False,
            rating=5
        )


@pytest.fixture
def setup_visited_cities_20_cities_in_1_region():
    for number in range(1, 21):
        VisitedCity.objects.create(
            user=User.objects.get(id=1),
            region=Region.objects.get(id=1),
            city=City.objects.get(id=number),
            has_magnet=False,
            rating=5
        )
