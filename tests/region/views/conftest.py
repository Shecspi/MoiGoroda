import pytest
from django.contrib.auth.models import User

from django.db import transaction

from region.models import Area, Region
from city.models import City, VisitedCity


symbols = 'АБВГДЕЖЗИЙКЛМНОПРСТУ'


@pytest.fixture
def create_user(client, django_user_model):
    new_user = django_user_model.objects.create_user(
        username='username', password='password'
    )
    return new_user


@pytest.fixture
def setup_db():
    """
    Создаёт 20 записей в таблице 'Region' и 20 в 'City' (все с 1 регионом).
    """
    area = Area.objects.create(title='Area 1')
    with transaction.atomic():
        # Создаём 20 регионов
        for symbol in symbols:
            Region.objects.create(
                area=area,
                title=f'Регион {symbol}',
                type='O',
                iso3166=f'RU-{symbol}'
            )
        # Создаём 20 городов в регионе с `id` = 1
        for symbol in symbols:
            City.objects.create(
                title=f'Город {symbol}',
                region=Region.objects.get(id=1),
                coordinate_width=55.55,
                coordinate_longitude=66.66
            )
        # Создаём 20 городов в регионе с `id` = 2
        for symbol in symbols:
            City.objects.create(
                title=f'Город {symbol}{symbol}',
                region=Region.objects.get(id=2),
                coordinate_width=55.55,
                coordinate_longitude=66.66
            )


@pytest.fixture
def setup_visited_cities_10_cities():
    """
    Создаёт 10 записей в таблице 'VisitedCity' в регионе с `id` = 1.
    """
    for number in range(1, 11):
        VisitedCity.objects.create(
            user=User.objects.get(id=1),
            region=Region.objects.get(id=1),
            city=City.objects.get(id=number),
            has_magnet=False,
            rating=5
        )


@pytest.fixture
def setup_20_visited_cities_in_1_region():
    """
    Создаёт 18 записей в таблице 'VisitedCity' в регионе с `id` = 1.
    """
    for number in range(1, 19):
        VisitedCity.objects.create(
            user=User.objects.get(id=1),
            region=Region.objects.get(id=1),
            city=City.objects.get(id=number),
            has_magnet=False,
            rating=5
        )
