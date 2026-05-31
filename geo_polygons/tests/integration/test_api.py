from __future__ import annotations

import json
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from geo_polygons.domain.services import GetPolygonService
from geo_polygons.infrastructure.models import OSMPolygonCache
from geo_polygons.infrastructure.repository import DjangoPolygonRepository
from geo_polygons.tests.conftest import RELATION_ID, make_polygon, response_json


def _polygon_url(relation_id: int = RELATION_ID) -> str:
    return reverse('api__geo_polygon', kwargs={'relation_id': relation_id})


def _download_url(relation_id: int = RELATION_ID) -> str:
    return reverse('api__geo_polygon_download', kwargs={'relation_id': relation_id})


@pytest.mark.integration
@pytest.mark.django_db
def test_get_polygon_requires_authentication(client: Client) -> None:
    response = client.get(_polygon_url())

    assert response.status_code == 401
    assert response_json(response) == {'detail': 'Требуется авторизация'}


@pytest.mark.integration
@pytest.mark.django_db
def test_get_polygon_returns_feature_for_authenticated_user(
    client: Client,
    user: User,
    cached_polygon: OSMPolygonCache,
) -> None:
    client.force_login(user)

    response = client.get(_polygon_url())

    assert response.status_code == 200
    data = response_json(response)
    assert data['type'] == 'Feature'
    assert data['geometry'] == cached_polygon.geojson
    assert data['properties']['relation_id'] == RELATION_ID
    assert data['properties']['name'] == cached_polygon.name


@pytest.mark.integration
@pytest.mark.django_db
def test_get_polygon_returns_404_when_not_found(
    client: Client,
    user: User,
    mocker: Any,
) -> None:
    client.force_login(user)
    service = mocker.Mock()
    service.execute.return_value = None
    mocker.patch('geo_polygons.api._get_polygon_service', return_value=service)

    response = client.get(_polygon_url())

    assert response.status_code == 404
    assert response_json(response) == {'detail': 'Полигон не найден'}


@pytest.mark.integration
@pytest.mark.django_db
def test_get_polygon_fetches_from_external_service_and_caches(
    client: Client,
    user: User,
    mocker: Any,
) -> None:
    client.force_login(user)
    polygon = make_polygon(name='Fetched polygon')
    external = mocker.Mock()
    external.fetch_polygon.return_value = polygon
    service = GetPolygonService(
        repository=DjangoPolygonRepository(),
        external_service=external,
    )
    mocker.patch('geo_polygons.api._get_polygon_service', return_value=service)

    response = client.get(_polygon_url())

    assert response.status_code == 200
    assert response_json(response)['properties']['name'] == 'Fetched polygon'
    assert OSMPolygonCache.objects.filter(relation_id=RELATION_ID).exists()
    external.fetch_polygon.assert_called_once_with(RELATION_ID)


@pytest.mark.integration
@pytest.mark.django_db
def test_download_requires_authentication(client: Client, cached_polygon: OSMPolygonCache) -> None:
    response = client.get(_download_url())

    assert response.status_code == 401
    assert response_json(response) == {'detail': 'Требуется авторизация'}


@pytest.mark.integration
@pytest.mark.django_db
def test_download_requires_advanced_premium(
    client: Client,
    user: User,
    cached_polygon: OSMPolygonCache,
) -> None:
    client.force_login(user)

    response = client.get(_download_url())

    assert response.status_code == 403
    assert response_json(response) == {
        'detail': 'Требуется расширенная подписка для скачивания',
    }


@pytest.mark.integration
@pytest.mark.django_db
def test_download_returns_404_when_polygon_missing(
    client: Client,
    premium_user: User,
    mocker: Any,
) -> None:
    client.force_login(premium_user)
    service = mocker.Mock()
    service.execute.return_value = None
    mocker.patch('geo_polygons.api._get_polygon_service', return_value=service)

    response = client.get(_download_url())

    assert response.status_code == 404
    assert response_json(response) == {'detail': 'Полигон не найден'}


@pytest.mark.integration
@pytest.mark.django_db
def test_download_returns_geojson_attachment_for_premium_user(
    client: Client,
    premium_user: User,
    cached_polygon: OSMPolygonCache,
) -> None:
    client.force_login(premium_user)

    response = client.get(_download_url())

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/geo+json'
    assert 'attachment' in response['Content-Disposition']
    assert response['Content-Disposition'].endswith('Moscow Oblast.geojson"')

    payload = json.loads(response.content.decode())
    assert payload['type'] == 'Feature'
    assert payload['properties']['relation_id'] == RELATION_ID


@pytest.mark.integration
@pytest.mark.django_db
def test_download_sanitizes_filename(
    client: Client,
    premium_user: User,
) -> None:
    OSMPolygonCache.objects.create(
        relation_id=RELATION_ID,
        name='Bad<>:"/\\|?*name',
        geojson=make_polygon().geometry,
    )
    client.force_login(premium_user)

    response = client.get(_download_url())

    assert response.status_code == 200
    assert 'filename="Bad_________name.geojson"' in response['Content-Disposition']
