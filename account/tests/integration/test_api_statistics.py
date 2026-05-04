from typing import Any

import pytest

from account.models import ShareSettings
from city.models import City, VisitedCity
from country.models import Country


@pytest.mark.integration
@pytest.mark.django_db
def test_personal_visited_cities_overview_returns_zero_ranks_without_data(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    response = client.get('/api/account/stats/visited_cities/overview/')

    assert response.status_code == 200
    data = response.json()
    assert data['unique_visited_cities']['count'] == 0
    assert data['unique_visited_cities_rank'] == 0
    assert data['total_visited_cities_visits']['count'] == 0
    assert data['total_visited_cities_visits_rank'] == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_regions_visited_cities_countries_returns_current_user_countries(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    other_user = django_user_model.objects.create_user(
        username='otheruser', password='password123'
    )
    russia = Country.objects.create(name='Россия', code='RU')
    georgia = Country.objects.create(name='Грузия', code='GE')
    moscow = City.objects.create(
        title='Москва',
        country=russia,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )
    tbilisi = City.objects.create(
        title='Тбилиси',
        country=georgia,
        coordinate_width=41.7151,
        coordinate_longitude=44.8271,
    )
    VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=True)
    VisitedCity.objects.create(user=other_user, city=tbilisi, rating=5, is_first_visit=True)

    client.force_login(user)
    response = client.get('/api/account/stats/regions/visited_cities_countries/')

    assert response.status_code == 200
    data = response.json()
    assert data['countries'] == [
        {
            'code': 'RU',
            'name': 'Россия',
            'number_of_visited_cities': 1,
            'number_of_cities': 1,
        }
    ]


@pytest.mark.integration
@pytest.mark.django_db
def test_regions_visited_cities_countries_uses_shared_user_id_for_public_dashboard(
    client: Any, django_user_model: Any
) -> None:
    owner = django_user_model.objects.create_user(username='owner', password='password123')
    viewer = django_user_model.objects.create_user(username='viewer', password='password123')
    ShareSettings.objects.create(user=owner, can_share=True, can_share_dashboard=True)
    russia = Country.objects.create(name='Россия', code='RU')
    georgia = Country.objects.create(name='Грузия', code='GE')
    moscow = City.objects.create(
        title='Москва',
        country=russia,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )
    tbilisi = City.objects.create(
        title='Тбилиси',
        country=georgia,
        coordinate_width=41.7151,
        coordinate_longitude=44.8271,
    )
    VisitedCity.objects.create(user=owner, city=moscow, rating=5, is_first_visit=True)
    VisitedCity.objects.create(user=viewer, city=tbilisi, rating=5, is_first_visit=True)

    response = client.get(
        f'/api/account/stats/regions/visited_cities_countries/?shared_user_id={owner.id}'
    )

    assert response.status_code == 200
    data = response.json()
    assert [country['code'] for country in data['countries']] == ['RU']
