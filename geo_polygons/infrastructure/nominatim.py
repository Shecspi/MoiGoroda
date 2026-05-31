from __future__ import annotations

import logging
import time
from typing import Any

import requests
from prometheus_client import Histogram

from geo_polygons.domain.entities import OSMPolygon
from geo_polygons.domain.interfaces import IExternalPolygonService

logger = logging.getLogger(__name__)

NOMINATIM_REQUEST_SECONDS = Histogram(
    'geo_polygons_nominatim_request_seconds',
    'Nominatim external API call latency',
    ['endpoint', 'status'],
)

NOMINATIM_ENDPOINTS = [
    'https://nominatim.openstreetmap.org/lookup',
    'https://nominatim.kumi.systems/lookup',
]
NOMINATIM_HEADERS = {
    'Accept-Language': 'en',
    'User-Agent': 'MoiGoroda/1.0 (https://moigoroda.ru)',
}


def _normalize_geometry(geometry: dict[str, Any]) -> dict[str, Any] | None:
    """Нормализует геометрию в валидный GeoJSON Polygon/MultiPolygon."""
    if not geometry:
        return None
    if geometry.get('type') in ('Point', 'Polygon', 'MultiPolygon'):
        return geometry
    if geometry.get('type') == 'LineString':
        coords = [list(c) for c in geometry['coordinates']]
        if len(coords) > 2:
            first, last = coords[0], coords[-1]
            if first[0] != last[0] or first[1] != last[1]:
                coords.append([first[0], first[1]])
        return {'type': 'Polygon', 'coordinates': [coords]}
    if geometry.get('type') == 'MultiLineString':
        polygons = []
        for line in geometry['coordinates']:
            copied_line = [list(c) for c in line]
            if len(copied_line) > 2:
                first, last = copied_line[0], copied_line[-1]
                if first[0] != last[0] or first[1] != last[1]:
                    copied_line.append([first[0], first[1]])
            polygons.append([copied_line])
        return {'type': 'MultiPolygon', 'coordinates': polygons}
    return geometry


class NominatimPolygonService(IExternalPolygonService):
    """Клиент Nominatim API с fallback на зеркала."""

    def fetch_polygon(self, relation_id: int) -> OSMPolygon | None:
        params = {
            'osm_ids': f'R{relation_id}',
            'format': 'json',
            'polygon_geojson': '1',
        }
        for endpoint in NOMINATIM_ENDPOINTS:
            start = time.monotonic()
            try:
                response = requests.get(
                    endpoint,
                    params=params,
                    headers=NOMINATIM_HEADERS,
                    timeout=8,
                )
                response.raise_for_status()
                results = response.json()
                if not results:
                    NOMINATIM_REQUEST_SECONDS.labels(
                        endpoint=endpoint,
                        status='empty',
                    ).observe(time.monotonic() - start)
                    return None

                result = results[0]
                raw_geometry = result.get('geojson')
                if not raw_geometry:
                    NOMINATIM_REQUEST_SECONDS.labels(
                        endpoint=endpoint,
                        status='no_geojson',
                    ).observe(time.monotonic() - start)
                    return None

                geometry = _normalize_geometry(raw_geometry)
                if geometry is None:
                    NOMINATIM_REQUEST_SECONDS.labels(
                        endpoint=endpoint,
                        status='invalid_geometry',
                    ).observe(time.monotonic() - start)
                    return None

                NOMINATIM_REQUEST_SECONDS.labels(
                    endpoint=endpoint,
                    status='success',
                ).observe(time.monotonic() - start)
                return OSMPolygon(
                    relation_id=relation_id,
                    name=result.get('display_name', '')[:500],
                    geometry=geometry,
                )
            except (requests.RequestException, ValueError) as e:
                NOMINATIM_REQUEST_SECONDS.labels(
                    endpoint=endpoint,
                    status='error',
                ).observe(time.monotonic() - start)
                logger.warning(
                    'Nominatim API error (%s) for relation %s: %s', endpoint, relation_id, e
                )
                continue

        logger.error('All Nominatim endpoints failed for relation %s', relation_id)
        return None
