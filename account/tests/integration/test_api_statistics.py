from datetime import date
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

    response = client.get('/api/account/stats/visited-cities/overview/')

    assert response.status_code == 200
    data = response.json()
    assert data['unique_visited_cities']['count'] == 0
    assert data['unique_visited_cities_rank'] == 0
    assert data['total_visited_cities_visits']['count'] == 0
    assert data['total_visited_cities_visits_rank'] == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_account_statistics_api_uses_hyphenated_paths(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    paths = [
        '/api/account/stats/visited-cities/overview/',
        '/api/account/stats/visited-cities/countries-coverage/',
        '/api/account/stats/visited-cities/countries-visits/',
        '/api/account/stats/regions/countries-coverage/',
        '/api/account/stats/regions/visited-cities-treemap/',
        '/api/account/stats/regions/visited-cities-countries/',
        '/api/account/stats/visited-countries/overview/',
    ]

    for path in paths:
        response = client.get(path)

        assert response.status_code == 200, path


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
    response = client.get('/api/account/stats/regions/visited-cities-countries/')

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
        f'/api/account/stats/regions/visited-cities-countries/?shared_user_id={owner.id}'
    )

    assert response.status_code == 200
    data = response.json()
    assert [country['code'] for country in data['countries']] == ['RU']


@pytest.mark.integration
@pytest.mark.django_db
def test_visited_cities_countries_coverage_rank_counts_only_users_with_more_unique_cities(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    leader = django_user_model.objects.create_user(username='leader', password='password123')
    equal_user = django_user_model.objects.create_user(username='equal', password='password123')
    country = Country.objects.create(name='Россия', code='RU')
    cities = [
        City.objects.create(
            title=f'Город {index}',
            country=country,
            coordinate_width=55.0 + index,
            coordinate_longitude=37.0 + index,
        )
        for index in range(4)
    ]
    VisitedCity.objects.create(user=user, city=cities[0], rating=5, is_first_visit=True)
    VisitedCity.objects.create(user=user, city=cities[1], rating=5, is_first_visit=True)
    VisitedCity.objects.create(user=leader, city=cities[0], rating=5, is_first_visit=True)
    VisitedCity.objects.create(user=leader, city=cities[1], rating=5, is_first_visit=True)
    VisitedCity.objects.create(user=leader, city=cities[2], rating=5, is_first_visit=True)
    VisitedCity.objects.create(user=equal_user, city=cities[0], rating=5, is_first_visit=True)
    VisitedCity.objects.create(user=equal_user, city=cities[1], rating=5, is_first_visit=True)

    client.force_login(user)
    response = client.get('/api/account/stats/visited-cities/countries-coverage/')

    assert response.status_code == 200
    data = response.json()
    assert data['countries_coverage'][0]['visited_cities'] == 2
    assert data['countries_coverage'][0]['rank'] == 2


@pytest.mark.integration
@pytest.mark.django_db
def test_visited_cities_countries_visits_rank_counts_only_users_with_more_visits(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    leader = django_user_model.objects.create_user(username='leader', password='password123')
    equal_user = django_user_model.objects.create_user(username='equal', password='password123')
    country = Country.objects.create(name='Россия', code='RU')
    city = City.objects.create(
        title='Москва',
        country=country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )
    VisitedCity.objects.create(
        user=user, city=city, rating=5, date_of_visit=date(2024, 1, 1)
    )
    VisitedCity.objects.create(
        user=user, city=city, rating=5, date_of_visit=date(2024, 1, 2)
    )
    VisitedCity.objects.create(
        user=leader, city=city, rating=5, date_of_visit=date(2024, 1, 1)
    )
    VisitedCity.objects.create(
        user=leader, city=city, rating=5, date_of_visit=date(2024, 1, 2)
    )
    VisitedCity.objects.create(
        user=leader, city=city, rating=5, date_of_visit=date(2024, 1, 3)
    )
    VisitedCity.objects.create(
        user=equal_user, city=city, rating=5, date_of_visit=date(2024, 1, 1)
    )
    VisitedCity.objects.create(
        user=equal_user, city=city, rating=5, date_of_visit=date(2024, 1, 2)
    )

    client.force_login(user)
    response = client.get('/api/account/stats/visited-cities/countries-visits/')

    assert response.status_code == 200
    data = response.json()
    assert data['countries_visits'][0]['visits'] == 2
    assert data['countries_visits'][0]['rank'] == 2
