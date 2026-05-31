from __future__ import annotations

import copy
from typing import Any

import pytest

from geo_polygons.infrastructure.nominatim import _normalize_geometry


LINE_STRING_GEOMETRY: dict[str, Any] = {
    'type': 'LineString',
    'coordinates': [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]],
}

MULTI_LINE_STRING_GEOMETRY: dict[str, Any] = {
    'type': 'MultiLineString',
    'coordinates': [
        [[0.0, 0.0], [2.0, 0.0], [2.0, 2.0]],
        [[10.0, 10.0], [11.0, 10.0], [11.0, 11.0]],
    ],
}


@pytest.mark.unit
def test_normalize_geometry_linestring_is_idempotent_and_preserves_input() -> None:
    geometry = copy.deepcopy(LINE_STRING_GEOMETRY)
    original = copy.deepcopy(geometry)

    first = _normalize_geometry(geometry)
    second = _normalize_geometry(geometry)

    assert geometry == original
    assert first == second
    assert first is not geometry
    assert first == {
        'type': 'Polygon',
        'coordinates': [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 0.0]]],
    }
    assert len(first['coordinates'][0]) == 4


@pytest.mark.unit
def test_normalize_geometry_multilinestring_is_idempotent_and_preserves_input() -> None:
    geometry = copy.deepcopy(MULTI_LINE_STRING_GEOMETRY)
    original = copy.deepcopy(geometry)

    first = _normalize_geometry(geometry)
    second = _normalize_geometry(geometry)

    assert geometry == original
    assert first == second
    assert first is not geometry
    assert first == {
        'type': 'MultiPolygon',
        'coordinates': [
            [[[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 0.0]]],
            [[[10.0, 10.0], [11.0, 10.0], [11.0, 11.0], [10.0, 10.0]]],
        ],
    }
    assert len(first['coordinates'][0][0]) == 4
    assert len(first['coordinates'][1][0]) == 4


@pytest.mark.unit
def test_normalize_geometry_returns_none_for_empty_geometry() -> None:
    assert _normalize_geometry({}) is None


@pytest.mark.unit
def test_normalize_geometry_passes_through_point_polygon_multipolygon() -> None:
    point = {'type': 'Point', 'coordinates': [0.0, 0.0]}
    polygon = {'type': 'Polygon', 'coordinates': [[[0.0, 0.0], [1.0, 0.0], [0.0, 0.0]]]}
    multi = {'type': 'MultiPolygon', 'coordinates': [[[[0.0, 0.0], [1.0, 0.0], [0.0, 0.0]]]]}

    assert _normalize_geometry(point) == point
    assert _normalize_geometry(polygon) == polygon
    assert _normalize_geometry(multi) == multi


@pytest.mark.unit
def test_normalize_geometry_linestring_with_two_points_does_not_close_ring() -> None:
    geometry = {'type': 'LineString', 'coordinates': [[0.0, 0.0], [1.0, 0.0]]}

    result = _normalize_geometry(geometry)

    assert result == {'type': 'Polygon', 'coordinates': [[[0.0, 0.0], [1.0, 0.0]]]}


@pytest.mark.unit
def test_normalize_geometry_linestring_already_closed_does_not_duplicate_point() -> None:
    geometry = {
        'type': 'LineString',
        'coordinates': [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 0.0]],
    }

    result = _normalize_geometry(geometry)

    assert result is not None
    assert len(result['coordinates'][0]) == 4


@pytest.mark.unit
def test_normalize_geometry_unknown_type_returns_geometry_unchanged() -> None:
    geometry = {'type': 'GeometryCollection', 'geometries': []}

    assert _normalize_geometry(geometry) == geometry
