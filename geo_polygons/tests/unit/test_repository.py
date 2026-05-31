from __future__ import annotations

import threading
from typing import Any

import pytest
from django.db import IntegrityError, connection

from geo_polygons.domain.entities import OSMPolygon
from geo_polygons.infrastructure.models import OSMPolygonCache
from geo_polygons.infrastructure.repository import DjangoPolygonRepository

RELATION_ID = 42
POLYGON_GEOMETRY = {
    'type': 'Polygon',
    'coordinates': [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 0.0]]],
}
UPDATED_GEOMETRY = {
    'type': 'Polygon',
    'coordinates': [[[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 0.0]]],
}


def _make_polygon(
    *,
    name: str = 'Test polygon',
    geometry: dict[str, Any] | None = None,
) -> OSMPolygon:
    return OSMPolygon(
        relation_id=RELATION_ID,
        name=name,
        geometry=geometry or POLYGON_GEOMETRY,
    )


@pytest.mark.unit
@pytest.mark.django_db
def test_get_by_relation_id_returns_none_when_missing() -> None:
    assert DjangoPolygonRepository().get_by_relation_id(RELATION_ID) is None


@pytest.mark.unit
@pytest.mark.django_db
def test_get_by_relation_id_returns_domain_polygon(cached_polygon: OSMPolygonCache) -> None:
    polygon = DjangoPolygonRepository().get_by_relation_id(cached_polygon.relation_id)

    assert polygon is not None
    assert polygon.relation_id == cached_polygon.relation_id
    assert polygon.name == cached_polygon.name
    assert polygon.geometry == cached_polygon.geojson


@pytest.mark.unit
@pytest.mark.django_db
def test_save_updates_name_and_geojson_when_record_exists() -> None:
    repository = DjangoPolygonRepository()
    repository.save(_make_polygon(name='Initial name'))

    repository.save(_make_polygon(name='Updated name', geometry=UPDATED_GEOMETRY))

    cached = OSMPolygonCache.objects.get(relation_id=RELATION_ID)
    assert cached.name == 'Updated name'
    assert cached.geojson == UPDATED_GEOMETRY


@pytest.mark.unit
@pytest.mark.django_db
def test_save_handles_integrity_error_from_get_or_create(mocker: Any) -> None:
    OSMPolygonCache.objects.create(
        relation_id=RELATION_ID,
        name='Existing',
        geojson=POLYGON_GEOMETRY,
    )
    mocker.patch.object(
        OSMPolygonCache.objects,
        'get_or_create',
        side_effect=IntegrityError('duplicate key value violates unique constraint'),
    )

    polygon = _make_polygon(name='Updated after race', geometry=UPDATED_GEOMETRY)
    DjangoPolygonRepository().save(polygon)

    cached = OSMPolygonCache.objects.get(relation_id=RELATION_ID)
    assert cached.name == 'Updated after race'
    assert cached.geojson == UPDATED_GEOMETRY


@pytest.mark.unit
@pytest.mark.django_db
def test_concurrent_save_with_same_relation_id_does_not_raise() -> None:
    repository = DjangoPolygonRepository()
    polygon = _make_polygon(name='Concurrent polygon')
    errors: list[BaseException] = []

    def worker() -> None:
        try:
            repository.save(polygon)
        except BaseException as exc:
            errors.append(exc)
        finally:
            connection.close()

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert OSMPolygonCache.objects.filter(relation_id=RELATION_ID).count() == 1

    cached = OSMPolygonCache.objects.get(relation_id=RELATION_ID)
    assert cached.name == polygon.name
    assert cached.geojson == polygon.geometry
