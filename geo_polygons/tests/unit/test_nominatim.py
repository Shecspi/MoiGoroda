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
