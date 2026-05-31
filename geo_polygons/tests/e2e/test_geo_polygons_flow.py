from __future__ import annotations

import json
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from geo_polygons.domain.services import GetPolygonService
from geo_polygons.infrastructure.models import OSMPolygonCache
from geo_polygons.infrastructure.nominatim import NominatimPolygonService
from geo_polygons.infrastructure.repository import DjangoPolygonRepository
from geo_polygons.tests.conftest import RELATION_ID, make_polygon, response_json


@pytest.mark.e2e
@pytest.mark.django_db
def test_anonymous_user_can_open_page_but_cannot_access_polygon_api(client: Client) -> None:
    page = client.get(reverse('geo-polygons'))
    api = client.get(reverse('api__geo_polygon', kwargs={'relation_id': RELATION_ID}))
    download = client.get(reverse('api__geo_polygon_download', kwargs={'relation_id': RELATION_ID}))

    assert page.status_code == 200
    assert api.status_code == 401
    assert download.status_code == 401


@pytest.mark.e2e
@pytest.mark.django_db
def test_authenticated_user_views_polygon_and_download_is_blocked_without_premium(
    client: Client,
    user: User,
    mocker: Any,
) -> None:
    client.force_login(user)
    polygon = make_polygon()
    mocker.patch(
        'geo_polygons.api._get_polygon_service',
        return_value=GetPolygonService(
            repository=DjangoPolygonRepository(),
            external_service=mocker.Mock(fetch_polygon=mocker.Mock(return_value=polygon)),
        ),
    )

    view_response = client.get(reverse('api__geo_polygon', kwargs={'relation_id': RELATION_ID}))
    download_response = client.get(
        reverse('api__geo_polygon_download', kwargs={'relation_id': RELATION_ID}),
    )

    assert view_response.status_code == 200
    assert response_json(view_response)['properties']['name'] == polygon.name
    assert download_response.status_code == 403
    assert OSMPolygonCache.objects.filter(relation_id=RELATION_ID).exists()


@pytest.mark.e2e
@pytest.mark.django_db
def test_premium_user_full_view_and_download_flow(
    client: Client,
    premium_user: User,
    mocker: Any,
) -> None:
    client.force_login(premium_user)
    polygon = make_polygon(name='Premium Region')
    mocker.patch(
        'geo_polygons.api._get_polygon_service',
        return_value=GetPolygonService(
            repository=DjangoPolygonRepository(),
            external_service=mocker.Mock(fetch_polygon=mocker.Mock(return_value=polygon)),
        ),
    )

    page = client.get(reverse('geo-polygons'))
    view_response = client.get(reverse('api__geo_polygon', kwargs={'relation_id': RELATION_ID}))
    download_response = client.get(
        reverse('api__geo_polygon_download', kwargs={'relation_id': RELATION_ID}),
    )

    assert page.status_code == 200
    assert 'window.OSM_VIEWER_HAS_ADVANCED_PREMIUM = true' in page.content.decode()
    assert view_response.status_code == 200
    assert download_response.status_code == 200
    assert download_response['Content-Type'] == 'application/geo+json'
    assert 'attachment' in download_response['Content-Disposition']

    downloaded = json.loads(download_response.content.decode())
    assert downloaded == response_json(view_response)


@pytest.mark.e2e
@pytest.mark.django_db
def test_polygon_is_served_from_cache_on_second_request(
    client: Client,
    user: User,
    mocker: Any,
) -> None:
    client.force_login(user)
    external = mocker.Mock()
    external.fetch_polygon.return_value = make_polygon(name='Cached once')
    service = GetPolygonService(
        repository=DjangoPolygonRepository(),
        external_service=external,
    )
    mocker.patch('geo_polygons.api._get_polygon_service', return_value=service)
    url = reverse('api__geo_polygon', kwargs={'relation_id': RELATION_ID})

    first = client.get(url)
    second = client.get(url)

    assert first.status_code == 200
    assert second.status_code == 200
    external.fetch_polygon.assert_called_once()


@pytest.mark.e2e
@pytest.mark.django_db
def test_nominatim_fetch_persists_polygon_for_subsequent_api_calls(
    client: Client,
    user: User,
    mocker: Any,
) -> None:
    client.force_login(user)
    nominatim_response = mocker.Mock()
    nominatim_response.raise_for_status.return_value = None
    nominatim_response.json.return_value = [
        {
            'display_name': 'Persisted Region',
            'geojson': make_polygon(name='Persisted Region').geometry,
        },
    ]
    mocker.patch(
        'geo_polygons.infrastructure.nominatim.requests.get',
        return_value=nominatim_response,
    )
    service = GetPolygonService(
        repository=DjangoPolygonRepository(),
        external_service=NominatimPolygonService(),
    )
    mocker.patch('geo_polygons.api._get_polygon_service', return_value=service)

    response = client.get(reverse('api__geo_polygon', kwargs={'relation_id': RELATION_ID}))

    assert response.status_code == 200
    cached = OSMPolygonCache.objects.get(relation_id=RELATION_ID)
    assert cached.name == 'Persisted Region'
    assert response_json(response)['properties']['name'] == 'Persisted Region'
