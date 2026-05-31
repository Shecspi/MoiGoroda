from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests

from geo_polygons.infrastructure.nominatim import NOMINATIM_ENDPOINTS, NominatimPolygonService
from geo_polygons.tests.conftest import POLYGON_GEOMETRY, RELATION_ID


def _nominatim_response(
    *,
    display_name: str = 'Moscow Oblast, Russia',
    geojson: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        {
            'display_name': display_name,
            'geojson': geojson
            if geojson is not None
            else {'type': 'Polygon', 'coordinates': POLYGON_GEOMETRY['coordinates']},
        },
    ]


@pytest.mark.unit
def test_fetch_polygon_returns_osm_polygon_on_success(mocker: Any) -> None:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = _nominatim_response()
    mocker.patch('geo_polygons.infrastructure.nominatim.requests.get', return_value=response)

    polygon = NominatimPolygonService().fetch_polygon(RELATION_ID)

    assert polygon is not None
    assert polygon.relation_id == RELATION_ID
    assert polygon.name == 'Moscow Oblast, Russia'
    assert polygon.geometry['type'] == 'Polygon'


@pytest.mark.unit
def test_fetch_polygon_truncates_long_display_name(mocker: Any) -> None:
    long_name = 'x' * 600
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = _nominatim_response(display_name=long_name)
    mocker.patch('geo_polygons.infrastructure.nominatim.requests.get', return_value=response)

    polygon = NominatimPolygonService().fetch_polygon(RELATION_ID)

    assert polygon is not None
    assert len(polygon.name) == 500


@pytest.mark.unit
def test_fetch_polygon_returns_none_for_empty_results(mocker: Any) -> None:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = []
    mocker.patch('geo_polygons.infrastructure.nominatim.requests.get', return_value=response)

    assert NominatimPolygonService().fetch_polygon(RELATION_ID) is None


@pytest.mark.unit
def test_fetch_polygon_returns_none_without_geojson(mocker: Any) -> None:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = [{'display_name': 'Test', 'geojson': None}]
    mocker.patch('geo_polygons.infrastructure.nominatim.requests.get', return_value=response)

    assert NominatimPolygonService().fetch_polygon(RELATION_ID) is None


@pytest.mark.unit
def test_fetch_polygon_tries_next_endpoint_after_request_error(mocker: Any) -> None:
    success = MagicMock()
    success.raise_for_status.return_value = None
    success.json.return_value = _nominatim_response()
    get_mock = mocker.patch(
        'geo_polygons.infrastructure.nominatim.requests.get',
        side_effect=[requests.RequestException('timeout'), success],
    )

    polygon = NominatimPolygonService().fetch_polygon(RELATION_ID)

    assert polygon is not None
    assert get_mock.call_count == 2
    assert get_mock.call_args_list[0].args[0] == NOMINATIM_ENDPOINTS[0]
    assert get_mock.call_args_list[1].args[0] == NOMINATIM_ENDPOINTS[1]


@pytest.mark.unit
def test_fetch_polygon_returns_none_when_all_endpoints_fail(mocker: Any) -> None:
    mocker.patch(
        'geo_polygons.infrastructure.nominatim.requests.get',
        side_effect=requests.RequestException('down'),
    )

    assert NominatimPolygonService().fetch_polygon(RELATION_ID) is None


@pytest.mark.unit
def test_fetch_polygon_tries_next_endpoint_after_invalid_json(mocker: Any) -> None:
    invalid = MagicMock()
    invalid.raise_for_status.return_value = None
    invalid.json.side_effect = json.JSONDecodeError('Expecting value', '', 0)
    success = MagicMock()
    success.raise_for_status.return_value = None
    success.json.return_value = _nominatim_response()
    get_mock = mocker.patch(
        'geo_polygons.infrastructure.nominatim.requests.get',
        side_effect=[invalid, success],
    )

    polygon = NominatimPolygonService().fetch_polygon(RELATION_ID)

    assert polygon is not None
    assert get_mock.call_count == 2


@pytest.mark.unit
def test_fetch_polygon_returns_none_when_all_endpoints_return_invalid_json(mocker: Any) -> None:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.side_effect = json.JSONDecodeError('Expecting value', '', 0)
    mocker.patch('geo_polygons.infrastructure.nominatim.requests.get', return_value=response)

    assert NominatimPolygonService().fetch_polygon(RELATION_ID) is None
