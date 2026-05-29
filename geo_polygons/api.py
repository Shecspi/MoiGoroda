from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any

import requests
from dmr import Controller
from dmr.plugins.msgspec import MsgspecSerializer

from geo_polygons.models import OSMPolygonCache
from premium.services.access import has_advanced_premium

logger = logging.getLogger(__name__)

NOMINATIM_ENDPOINTS = [
    'https://nominatim.openstreetmap.org/lookup',
    'https://nominatim.kumi.systems/lookup',
]
NOMINATIM_HEADERS = {
    'Accept-Language': 'en',
    'User-Agent': 'MoiGoroda/1.0 (https://moigoroda.ru)',
}


def _fetch_polygon_from_nominatim(relation_id: int) -> dict | None:
    params = {
        'osm_ids': f'R{relation_id}',
        'format': 'json',
        'polygon_geojson': '1',
    }
    for endpoint in NOMINATIM_ENDPOINTS:
        try:
            response = requests.get(
                endpoint,
                params=params,
                headers=NOMINATIM_HEADERS,
                timeout=15,
            )
            response.raise_for_status()
            results = response.json()
            return results[0] if results else None
        except requests.RequestException as e:
            logger.warning('Nominatim API error (%s) for relation %s: %s', endpoint, relation_id, e)
            continue
    logger.error('All Nominatim endpoints failed for relation %s', relation_id)
    return None


def _normalize_geometry(geometry: dict) -> dict | None:
    if not geometry:
        return None
    if geometry.get('type') in ('Point', 'Polygon', 'MultiPolygon'):
        return geometry
    if geometry.get('type') == 'LineString':
        coords = geometry['coordinates']
        if len(coords) > 2:
            first, last = coords[0], coords[-1]
            if first[0] != last[0] or first[1] != last[1]:
                coords.append([first[0], first[1]])
        return {'type': 'Polygon', 'coordinates': [coords]}
    if geometry.get('type') == 'MultiLineString':
        polygons = []
        for line in geometry['coordinates']:
            if len(line) > 2:
                first, last = line[0], line[-1]
                if first[0] != last[0] or first[1] != last[1]:
                    line.append([first[0], first[1]])
            polygons.append([line])
        return {'type': 'MultiPolygon', 'coordinates': polygons}
    return geometry


class GetOSMPolygonController(Controller[MsgspecSerializer]):
    @staticmethod
    def _build_response(geometry: dict, name: str, relation_id: int) -> dict[str, Any]:
        return {
            'type': 'Feature',
            'geometry': geometry,
            'properties': {
                'name': name,
                'relation_id': relation_id,
            },
        }

    def get(self) -> Any:
        if not self.request.user.is_authenticated:
            return self.to_response(
                raw_data={'detail': 'Требуется авторизация'},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        relation_id = self.kwargs['relation_id']
        is_download = self.request.GET.get('download') == '1'

        if is_download and not has_advanced_premium(self.request.user):
            return self.to_response(
                raw_data={'detail': 'Требуется расширенная подписка для скачивания'},
                status_code=HTTPStatus.FORBIDDEN,
            )

        cached = OSMPolygonCache.objects.filter(relation_id=relation_id).first()
        if cached:
            return self.to_response(
                raw_data=self._build_response(cached.geojson, cached.name, relation_id),
            )

        nominatim_result = _fetch_polygon_from_nominatim(relation_id)
        if not nominatim_result or not nominatim_result.get('geojson'):
            return self.to_response(
                raw_data={'detail': 'Полигон не найден'},
                status_code=HTTPStatus.NOT_FOUND,
            )

        geometry = _normalize_geometry(nominatim_result['geojson'])
        if not geometry:
            return self.to_response(
                raw_data={'detail': 'Не удалось обработать геометрию'},
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        OSMPolygonCache.objects.create(
            relation_id=relation_id,
            name=nominatim_result.get('display_name', '')[:500],
            geojson=geometry,
        )

        return self.to_response(
            raw_data=self._build_response(
                geometry, nominatim_result.get('display_name', ''), relation_id
            ),
        )
