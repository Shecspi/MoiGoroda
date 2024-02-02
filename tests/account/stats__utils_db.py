import pytest

from datetime import datetime

from city.models import City, VisitedCity
from region.models import Area, Region
from services.db.visited_city import get_number_of_visited_cities


@pytest.fixture
def setup(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    for num in range(1, 6):
        city = City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)
        VisitedCity.objects.create(
            user=user, region=region, city=city,
            date_of_visit=f"{datetime.now().year - num}-01-01", has_magnet=False, rating=3
        )


@pytest.mark.django_db
def test__get_number_of_visited_cities_for_existing_user(setup):
    assert get_number_of_visited_cities(user_id=1) == 5


@pytest.mark.django_db
def test__get_number_of_visited_cities_for_not_existing_user(setup):
    assert get_number_of_visited_cities(user_id=2) == 0
