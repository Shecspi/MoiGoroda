from __future__ import annotations

from geo_polygons.domain.entities import OSMPolygon
from geo_polygons.domain.interfaces import IPolygonRepository
from geo_polygons.infrastructure.models import OSMPolygonCache


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
        OSMPolygonCache.objects.create(
            relation_id=polygon.relation_id,
            name=polygon.name,
            geojson=polygon.geometry,
        )
