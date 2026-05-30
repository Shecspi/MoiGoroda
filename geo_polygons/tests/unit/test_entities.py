from __future__ import annotations

import pytest

from geo_polygons.tests.conftest import POLYGON_GEOMETRY, RELATION_ID, make_polygon


@pytest.mark.unit
def test_osm_polygon_to_geojson_feature() -> None:
    polygon = make_polygon(name='Test Region', relation_id=RELATION_ID)

    feature = polygon.to_geojson_feature()

    assert feature == {
        'type': 'Feature',
        'geometry': POLYGON_GEOMETRY,
        'properties': {
            'name': 'Test Region',
            'relation_id': RELATION_ID,
        },
    }


@pytest.mark.unit
def test_osm_polygon_is_immutable() -> None:
    polygon = make_polygon()

    with pytest.raises(AttributeError):
        polygon.name = 'Other'  # type: ignore[misc]
