import pytest

from datetime import datetime

from city.models import City, VisitedCity
from region.models import Area, Region
from services.db.visited_city import get_number_of_visited_cities, get_number_of_visited_cities_by_year, \
    get_number_of_not_visited_cities


@pytest.fixture
def setup(client, django_user_model):
    user = django_user_model.objects.create_user(id=1, username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    for num in range(1, 6):
        city = City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)
        VisitedCity.objects.create(
            user=user, region=region, city=city,
            date_of_visit=f"{datetime.now().year}-01-01", has_magnet=False, rating=3
        )
    City.objects.create(title='Город 6', region=region, coordinate_width=1, coordinate_longitude=1)


@pytest.mark.django_db
def test__get_number_of_visited_cities_for_existing_user(setup):
    assert get_number_of_visited_cities(user_id=1) == 5


@pytest.mark.django_db
def test__get_number_of_visited_cities_for_not_existing_user(setup):
    assert get_number_of_visited_cities(user_id=2) == 0


@pytest.mark.django_db
def test__get_number_of_not_visited_cities(setup):
    assert get_number_of_not_visited_cities(user_id=1) == 1


@pytest.mark.django_db
def test__get_number_of_visited_cities_by_year_current_year(setup):
    assert get_number_of_visited_cities_by_year(user_id=1, year=datetime.now().year) == 5


@pytest.mark.django_db
def test__get_number_of_visited_cities_by_year_prev_year(setup):
    assert get_number_of_visited_cities_by_year(user_id=1, year=datetime.now().year - 1) == 0
