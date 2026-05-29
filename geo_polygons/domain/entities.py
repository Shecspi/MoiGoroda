from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GeoJSONGeometry:
    """Доменная модель геометрии GeoJSON."""

    type: str
    coordinates: list[Any]


@dataclass(frozen=True)
class OSMPolygon:
    """Доменная модель OSM полигона."""

    relation_id: int
    name: str
    geometry: dict[str, Any]

    def to_geojson_feature(self) -> dict[str, Any]:
        return {
            'type': 'Feature',
            'geometry': self.geometry,
            'properties': {
                'name': self.name,
                'relation_id': self.relation_id,
            },
        }
