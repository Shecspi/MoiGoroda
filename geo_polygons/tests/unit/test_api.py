from __future__ import annotations

import pytest

from geo_polygons.api import _safe_geojson_filename


@pytest.mark.unit
@pytest.mark.parametrize(
    ('raw_name', 'expected'),
    [
        ('Moscow Oblast', 'Moscow Oblast'),
        ('  Trimmed  ', 'Trimmed'),
        ('Bad<>:"/\\|?*name', 'Bad_________name'),
        ('', 'osm_object'),
        ('   ', 'osm_object'),
    ],
)
def test_safe_geojson_filename(raw_name: str, expected: str) -> None:
    assert _safe_geojson_filename(raw_name) == expected
