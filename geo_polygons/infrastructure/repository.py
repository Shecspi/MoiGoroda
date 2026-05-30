from __future__ import annotations

import logging

from django.db import IntegrityError

from geo_polygons.domain.entities import OSMPolygon
from geo_polygons.domain.interfaces import IPolygonRepository
from geo_polygons.infrastructure.models import OSMPolygonCache

logger = logging.getLogger(__name__)


class DjangoPolygonRepository(IPolygonRepository):
    """Django ORM реализация репозитория полигонов."""

    def get_by_relation_id(self, relation_id: int) -> OSMPolygon | None:
        cached = OSMPolygonCache.objects.filter(relation_id=relation_id).first()
        if cached is None:
            return None
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
