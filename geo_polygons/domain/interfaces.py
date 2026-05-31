from __future__ import annotations

from abc import ABC, abstractmethod

from geo_polygons.domain.entities import OSMPolygon


class IPolygonRepository(ABC):
    """Интерфейс репозитория полигонов."""

    @abstractmethod
    def get_by_relation_id(self, relation_id: int) -> OSMPolygon | None:
        """Получить полигон из кеша по relation_id."""

    @abstractmethod
    def save(self, polygon: OSMPolygon) -> None:
        """Сохранить полигон в кеш."""


class IExternalPolygonService(ABC):
    """Интерфейс внешнего сервиса полигонов (Nominatim)."""

    @abstractmethod
    def fetch_polygon(self, relation_id: int) -> OSMPolygon | None:
        """Запросить полигон из внешнего API."""
