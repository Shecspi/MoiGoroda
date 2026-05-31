from __future__ import annotations

import logging

from django.db import IntegrityError
from prometheus_client import Counter

from geo_polygons.domain.entities import OSMPolygon
from geo_polygons.domain.interfaces import IPolygonRepository
from geo_polygons.infrastructure.models import OSMPolygonCache

logger = logging.getLogger(__name__)

POLYGON_CACHE_REQUESTS = Counter(
    'geo_polygons_cache_requests_total',
    'OSM polygon cache lookups',
    ['result'],
)


class DjangoPolygonRepository(IPolygonRepository):
    """Django ORM реализация репозитория полигонов."""

    def get_by_relation_id(self, relation_id: int) -> OSMPolygon | None:
        try:
            cached = OSMPolygonCache.objects.get(relation_id=relation_id)
        except OSMPolygonCache.DoesNotExist:
            POLYGON_CACHE_REQUESTS.labels(result='miss').inc()
            return None
        POLYGON_CACHE_REQUESTS.labels(result='hit').inc()
        return OSMPolygon(
            relation_id=cached.relation_id,
            name=cached.name,
            geometry=cached.geojson,
        )

    def save(self, polygon: OSMPolygon) -> None:
        try:
            cached, created = OSMPolygonCache.objects.get_or_create(
                relation_id=polygon.relation_id,
                defaults={
                    'name': polygon.name,
                    'geojson': polygon.geometry,
                },
            )
        except IntegrityError:
            logger.warning(
                'Concurrent OSMPolygonCache save for relation_id=%s, using existing row',
                polygon.relation_id,
            )
            cached = OSMPolygonCache.objects.get(relation_id=polygon.relation_id)
            created = False

        if not created:
            self._sync_cached_fields(cached, polygon)

    def _sync_cached_fields(self, cached: OSMPolygonCache, polygon: OSMPolygon) -> None:
        updated_fields: list[str] = []
        if cached.name != polygon.name:
            cached.name = polygon.name
            updated_fields.append('name')
        if cached.geojson != polygon.geometry:
            cached.geojson = polygon.geometry
            updated_fields.append('geojson')
        if updated_fields:
            cached.save(update_fields=updated_fields)
