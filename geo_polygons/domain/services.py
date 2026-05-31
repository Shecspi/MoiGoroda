from __future__ import annotations

from geo_polygons.domain.entities import OSMPolygon
from geo_polygons.domain.interfaces import IExternalPolygonService, IPolygonRepository


class GetPolygonService:
    """
    Use case: получить полигон OSM.
    Сначала проверяет кеш, затем запрашивает внешний API и кеширует результат.
    """

    def __init__(
        self,
        repository: IPolygonRepository,
        external_service: IExternalPolygonService,
    ) -> None:
        self._repository = repository
        self._external_service = external_service

    def execute(self, relation_id: int) -> OSMPolygon | None:
        cached = self._repository.get_by_relation_id(relation_id)
        if cached is not None:
            return cached

        fetched = self._external_service.fetch_polygon(relation_id)
        if fetched is None:
            return None

        self._repository.save(fetched)
        return fetched
