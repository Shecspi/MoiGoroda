"""Проверка записи analytics.VisitedCityAddSource при добавлении посещения."""

from datetime import date
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from analytics.models import VisitedCityAddSource
from city.models import City, VisitedCity
from country.models import Country
from region.models import Area, Region, RegionType


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_api_add_visit_writes_region_map_surface(
    api_client: APIClient, django_user_model: type[User]
) -> None:
    user = django_user_model.objects.create_user(username='u1', password='pw')
    api_client.force_authenticate(user=user)
    country = Country.objects.create(name='ATL', code='AA')
    city = City.objects.create(
        title='T',
        country=country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )

    url = reverse('api__add_visited_city')
    response = api_client.post(
        url,
        data={
            'city': city.pk,
            'date_of_visit': date(2026, 5, 6).isoformat(),
            'rating': 5,
            'from': 'region_map',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    vc = VisitedCity.objects.get(user=user, city=city)
    row = VisitedCityAddSource.objects.get(visited_city=vc)
    assert row.surface == VisitedCityAddSource.Surface.REGION_MAP
    assert row.raw_hint == ''


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_api_add_visit_unknown_from_records_api_unknown_with_raw_hint(
    api_client: APIClient, django_user_model: type[User]
) -> None:
    user = django_user_model.objects.create_user(username='u2', password='pw')
    api_client.force_authenticate(user=user)
    country = Country.objects.create(name='AT2', code='BB')
    city = City.objects.create(
        title='Y',
        country=country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )

    url = reverse('api__add_visited_city')
    response = api_client.post(
        url,
        data={
            'city': city.pk,
            'date_of_visit': date(2026, 5, 7).isoformat(),
            'rating': 5,
            'from': 'random client string',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    vc = VisitedCity.objects.get(user=user, city=city)
    row = VisitedCityAddSource.objects.get(visited_city=vc)
    assert row.surface == VisitedCityAddSource.Surface.API_UNKNOWN
    assert row.raw_hint == 'random client string'


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_api_country_map_string_is_api_unknown_with_hint(
    api_client: APIClient, django_user_model: type[User]
) -> None:
    """Строка с карты стран относится к другому API; для города — api_unknown + raw_hint."""
    user = django_user_model.objects.create_user(username='u4', password='pw')
    api_client.force_authenticate(user=user)
    country = Country.objects.create(name='AT4', code='DD')
    city = City.objects.create(
        title='W',
        country=country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )

    url = reverse('api__add_visited_city')
    response = api_client.post(
        url,
        data={
            'city': city.pk,
            'date_of_visit': date(2026, 5, 9).isoformat(),
            'rating': 5,
            'from': 'country map',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    vc = VisitedCity.objects.get(user=user, city=city)
    row = VisitedCityAddSource.objects.get(visited_city=vc)
    assert row.surface == VisitedCityAddSource.Surface.API_UNKNOWN
    assert row.raw_hint == 'country map'


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_api_general_map_alias_maps_to_visited_cities_map(
    api_client: APIClient, django_user_model: type[User]
) -> None:
    user = django_user_model.objects.create_user(username='u3', password='pw')
    api_client.force_authenticate(user=user)
    country = Country.objects.create(name='AT3', code='CC')
    city = City.objects.create(
        title='Z',
        country=country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )

    url = reverse('api__add_visited_city')
    response = api_client.post(
        url,
        data={
            'city': city.pk,
            'date_of_visit': date(2026, 5, 8).isoformat(),
            'rating': 5,
            'from': 'general map',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    vc = VisitedCity.objects.get(user=user, city=city)
    row = VisitedCityAddSource.objects.get(visited_city=vc)
    assert row.surface == VisitedCityAddSource.Surface.VISITED_CITIES_MAP


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@patch('city.signals.notify_subscribers_on_city_add')
@patch('city.services.db.set_is_visit_first_for_all_visited_cities')
def test_city_create_html_records_sidebar_surface(
    mock_set_first: object,
    mock_signal: object,
    client: Client,
    django_user_model: type[User],
) -> None:
    user = django_user_model.objects.create_user(username='htm', password='pw')

    country = Country.objects.create(name='HC', code='H1')
    region_type, _ = RegionType.objects.get_or_create(title='тип')
    area = Area.objects.create(country=country, title='A')
    region = Region.objects.create(
        country=country,
        area=area,
        title='R',
        type=region_type,
        iso3166='H-R',
        full_name='Rf',
    )
    city_obj = City.objects.create(
        title='HtmlCity',
        country=country,
        region=region,
        coordinate_width=55.1,
        coordinate_longitude=37.1,
    )

    client.login(username='htm', password='pw')

    form_data = {
        'country': country.id,
        'region': region.id,
        'city': city_obj.id,
        'rating': '5',
        'analytics_surface': 'sidebar',
    }

    response = client.post(reverse('city-create'), data=form_data)

    assert response.status_code == 302
    vc = VisitedCity.objects.get(user=user, city=city_obj)
    row = VisitedCityAddSource.objects.get(visited_city=vc)
    assert row.surface == VisitedCityAddSource.Surface.SIDEBAR
