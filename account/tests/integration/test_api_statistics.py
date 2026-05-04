from datetime import date
from typing import Any

import pytest

from account.api import normalize_treemap_country_code
from account.models import ShareSettings
from city.models import City, VisitedCity
from country.models import Country, Location, PartOfTheWorld, VisitedCountry
from region.models import Area, Region, RegionType


def create_country(name: str, code: str, location: Location | None = None) -> Country:
    return Country.objects.create(name=name, code=code, location=location)


def create_city(
    title: str,
    country: Country,
    region: Region | None = None,
    index: int = 0,
) -> City:
    return City.objects.create(
        title=title,
        country=country,
        region=region,
        coordinate_width=55.0 + index,
        coordinate_longitude=37.0 + index,
    )


def create_region(country: Country, title: str, iso3166: str) -> Region:
    region_type, _ = RegionType.objects.get_or_create(title='область')
    area, _ = Area.objects.get_or_create(country=country, title=f'{country.code} округ')
    return Region.objects.create(
        country=country,
        area=area,
        title=title,
        type=region_type,
        full_name=f'{title} область',
        iso3166=iso3166,
    )


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        (None, 'RU'),
        ('', 'RU'),
        ('   ', 'RU'),
        ('GE', 'GE'),
        ('geo', 'GEO'),
        ('RUML', 'RUM'),
        ('RU-junk-extra', 'RU'),
        ('12', 'RU'),
    ],
)
def test_normalize_treemap_country_code(raw: str | None, expected: str) -> None:
    assert normalize_treemap_country_code(raw) == expected


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
    assert data['new_visited_cities']['count'] == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_account_statistics_api_uses_hyphenated_paths(client: Any, django_user_model: Any) -> None:
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
@pytest.mark.parametrize(
    'query_string',
    [
        '',
        '?shared_user_id=abc',
        '?shared_user_id=0',
        '?shared_user_id=-1',
    ],
)
def test_account_statistics_api_rejects_anonymous_or_invalid_shared_user_id(
    client: Any, query_string: str
) -> None:
    response = client.get(f'/api/account/stats/visited-cities/overview/{query_string}')

    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.django_db
@pytest.mark.parametrize(
    'share_settings',
    [
        None,
        {'can_share': False, 'can_share_dashboard': True},
        {'can_share': True, 'can_share_dashboard': False},
    ],
)
def test_account_statistics_api_rejects_not_public_shared_dashboard(
    client: Any, django_user_model: Any, share_settings: dict[str, bool] | None
) -> None:
    user = django_user_model.objects.create_user(username='shareduser', password='password123')
    if share_settings is not None:
        ShareSettings.objects.create(user=user, **share_settings)

    response = client.get(f'/api/account/stats/visited-cities/overview/?shared_user_id={user.id}')

    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.django_db
def test_visited_cities_overview_counts_visits_unique_new_series_and_ranks(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    leader = django_user_model.objects.create_user(username='leader', password='password123')
    equal_user = django_user_model.objects.create_user(username='equal', password='password123')
    country = create_country('Россия', 'RU')
    cities = [create_city(f'Город {index}', country, index=index) for index in range(4)]

    VisitedCity.objects.create(
        user=user, city=cities[0], rating=5, is_first_visit=True, date_of_visit=date(2025, 1, 1)
    )
    VisitedCity.objects.create(
        user=user, city=cities[1], rating=4, is_first_visit=True, date_of_visit=date(2025, 2, 1)
    )
    VisitedCity.objects.create(
        user=user, city=cities[0], rating=3, is_first_visit=False, date_of_visit=date(2025, 2, 2)
    )
    for index, city in enumerate(cities[:3], start=1):
        VisitedCity.objects.create(
            user=leader,
            city=city,
            rating=5,
            is_first_visit=True,
            date_of_visit=date(2025, 3, index),
        )
    VisitedCity.objects.create(
        user=leader,
        city=cities[0],
        rating=5,
        is_first_visit=False,
        date_of_visit=date(2025, 4, 1),
    )
    VisitedCity.objects.create(
        user=equal_user,
        city=cities[0],
        rating=5,
        is_first_visit=True,
        date_of_visit=date(2025, 1, 1),
    )
    VisitedCity.objects.create(
        user=equal_user,
        city=cities[1],
        rating=5,
        is_first_visit=True,
        date_of_visit=date(2025, 1, 2),
    )
    VisitedCity.objects.create(
        user=equal_user,
        city=cities[0],
        rating=5,
        is_first_visit=False,
        date_of_visit=date(2025, 1, 3),
    )

    client.force_login(user)
    response = client.get('/api/account/stats/visited-cities/overview/')

    assert response.status_code == 200
    data = response.json()
    assert data['unique_visited_cities']['count'] == 2
    assert data['total_visited_cities_visits']['count'] == 3
    assert data['unique_visited_cities_rank'] == 2
    assert data['total_visited_cities_visits_rank'] == 2
    assert data['unique_visited_cities_by_year'] == [{'label': '2025', 'count': 2}]
    assert data['total_visited_cities_visits_by_year'] == [{'label': '2025', 'count': 3}]
    assert data['new_visited_cities_by_year'] == [{'label': '2025', 'count': 2}]
    assert data['new_visited_cities']['count'] == 2
    assert {'label': '01.2025', 'count': 1} in data['unique_visited_cities_by_month']
    assert {'label': '02.2025', 'count': 2} in data['unique_visited_cities_by_month']
    assert {'label': '02.2025', 'count': 2} in data['total_visited_cities_visits_by_month']
    assert {'label': '02.2025', 'count': 1} in data['new_visited_cities_by_month']


@pytest.mark.integration
@pytest.mark.django_db
def test_regions_visited_cities_countries_returns_current_user_countries(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    other_user = django_user_model.objects.create_user(username='otheruser', password='password123')
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
def test_shared_statistics_endpoints_use_shared_owner_not_authenticated_viewer(
    client: Any, django_user_model: Any
) -> None:
    owner = django_user_model.objects.create_user(username='owner', password='password123')
    viewer = django_user_model.objects.create_user(username='viewer', password='password123')
    ShareSettings.objects.create(user=owner, can_share=True, can_share_dashboard=True)
    russia = create_country('Россия', 'RU')
    georgia = create_country('Грузия', 'GE')
    ru_region = create_region(russia, 'Московская', 'RU-MOS')
    moscow = create_city('Москва', russia, ru_region, index=1)
    spb = create_city('Санкт-Петербург', russia, ru_region, index=2)
    tbilisi = create_city('Тбилиси', georgia, index=3)

    VisitedCity.objects.create(user=owner, city=moscow, rating=5, is_first_visit=True)
    VisitedCity.objects.create(user=owner, city=spb, rating=5, is_first_visit=True)
    VisitedCity.objects.create(user=viewer, city=tbilisi, rating=5, is_first_visit=True)
    VisitedCountry.objects.create(user=owner, country=russia)
    VisitedCountry.objects.create(user=viewer, country=georgia)
    client.force_login(viewer)

    shared_query = f'?shared_user_id={owner.id}'
    overview = client.get(f'/api/account/stats/visited-cities/overview/{shared_query}').json()
    cities_coverage = client.get(
        f'/api/account/stats/visited-cities/countries-coverage/{shared_query}'
    ).json()
    cities_visits = client.get(
        f'/api/account/stats/visited-cities/countries-visits/{shared_query}'
    ).json()
    regions_coverage = client.get(
        f'/api/account/stats/regions/countries-coverage/{shared_query}'
    ).json()
    treemap = client.get(
        f'/api/account/stats/regions/visited-cities-treemap/{shared_query}&country_code=RU'
    ).json()
    countries = client.get(
        f'/api/account/stats/regions/visited-cities-countries/{shared_query}'
    ).json()
    visited_countries = client.get(
        f'/api/account/stats/visited-countries/overview/{shared_query}'
    ).json()

    assert overview['unique_visited_cities']['count'] == 2
    assert [item['name'] for item in cities_coverage['countries_coverage']] == ['Россия']
    assert [item['name'] for item in cities_visits['countries_visits']] == ['Россия']
    assert [item['name'] for item in regions_coverage['countries_coverage']] == ['Россия']
    assert treemap['items'] == [
        {
            'fullname': 'Московская область',
            'unique_visited_cities': 2,
            'total_cities': 2,
        }
    ]
    assert [item['code'] for item in countries['countries']] == ['RU']
    assert visited_countries['visited'] == 1


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
    VisitedCity.objects.create(user=user, city=city, rating=5, date_of_visit=date(2024, 1, 1))
    VisitedCity.objects.create(user=user, city=city, rating=5, date_of_visit=date(2024, 1, 2))
    VisitedCity.objects.create(user=leader, city=city, rating=5, date_of_visit=date(2024, 1, 1))
    VisitedCity.objects.create(user=leader, city=city, rating=5, date_of_visit=date(2024, 1, 2))
    VisitedCity.objects.create(user=leader, city=city, rating=5, date_of_visit=date(2024, 1, 3))
    VisitedCity.objects.create(user=equal_user, city=city, rating=5, date_of_visit=date(2024, 1, 1))
    VisitedCity.objects.create(user=equal_user, city=city, rating=5, date_of_visit=date(2024, 1, 2))

    client.force_login(user)
    response = client.get('/api/account/stats/visited-cities/countries-visits/')

    assert response.status_code == 200
    data = response.json()
    assert data['countries_visits'][0]['visits'] == 2
    assert data['countries_visits'][0]['rank'] == 2


@pytest.mark.integration
@pytest.mark.django_db
def test_regions_visited_cities_treemap_returns_regions_with_city_counts(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    country = create_country('Россия', 'RU')
    moscow_region = create_region(country, 'Московская', 'RU-MOS')
    tver_region = create_region(country, 'Тверская', 'RU-TVE')
    moscow = create_city('Москва', country, moscow_region, index=1)
    create_city('Коломна', country, moscow_region, index=2)
    create_city('Тверь', country, tver_region, index=3)
    VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=True)

    client.force_login(user)
    response = client.get('/api/account/stats/regions/visited-cities-treemap/?country_code=RU')

    assert response.status_code == 200
    data = response.json()
    assert data['items'] == [
        {
            'fullname': 'Московская область',
            'unique_visited_cities': 1,
            'total_cities': 2,
        },
        {
            'fullname': 'Тверская область',
            'unique_visited_cities': 0,
            'total_cities': 1,
        },
    ]


@pytest.mark.integration
@pytest.mark.django_db
def test_regions_visited_cities_treemap_falls_back_to_country_without_regions(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    country = create_country('Грузия', 'GE')
    tbilisi = create_city('Тбилиси', country)
    create_city('Батуми', country, index=2)
    VisitedCity.objects.create(user=user, city=tbilisi, rating=5, is_first_visit=True)

    client.force_login(user)
    response = client.get('/api/account/stats/regions/visited-cities-treemap/?country_code=GE')

    assert response.status_code == 200
    assert response.json()['items'] == [
        {
            'fullname': 'Грузия',
            'unique_visited_cities': 1,
            'total_cities': 2,
        }
    ]


@pytest.mark.integration
@pytest.mark.django_db
def test_regions_visited_cities_treemap_truncates_country_code_to_three_chars(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    country = create_country('Россия', 'RU')
    region = create_region(country, 'Московская', 'RU-MOS')
    moscow = create_city('Москва', country, region, index=1)
    VisitedCity.objects.create(user=user, city=moscow, rating=5, is_first_visit=True)

    client.force_login(user)
    response_short = client.get(
        '/api/account/stats/regions/visited-cities-treemap/?country_code=RU'
    )
    response_overflow = client.get(
        '/api/account/stats/regions/visited-cities-treemap/'
        '?country_code=RU-malicious-overflow-suffix-xxxxx'
    )

    assert response_short.status_code == 200
    assert response_overflow.status_code == 200
    assert response_short.json() == response_overflow.json()


@pytest.mark.integration
@pytest.mark.django_db
def test_visited_countries_overview_counts_totals_by_locations_for_current_user(
    client: Any, django_user_model: Any
) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    other_user = django_user_model.objects.create_user(username='other', password='password123')
    europe = PartOfTheWorld.objects.create(name='Европа')
    asia = PartOfTheWorld.objects.create(name='Азия')
    eastern_europe = Location.objects.create(name='Восточная Европа', part_of_the_world=europe)
    caucasus = Location.objects.create(name='Кавказ', part_of_the_world=asia)
    russia = create_country('Россия', 'RU', eastern_europe)
    georgia = create_country('Грузия', 'GE', caucasus)
    unknown_location = create_country('Страна без локации', 'ZZ')
    VisitedCountry.objects.create(user=user, country=russia)
    VisitedCountry.objects.create(user=user, country=unknown_location)
    VisitedCountry.objects.create(user=other_user, country=georgia)

    client.force_login(user)
    response = client.get('/api/account/stats/visited-countries/overview/')

    assert response.status_code == 200
    data = response.json()
    assert data['visited'] == 2
    assert data['total'] == 3
    assert data['by_location'] == [
        {'location_name': 'Азия', 'visited': 0, 'total': 1},
        {'location_name': 'Европа', 'visited': 1, 'total': 1},
    ]
