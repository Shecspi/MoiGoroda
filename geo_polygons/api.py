from __future__ import annotations

import json
import re
from http import HTTPStatus
from typing import Any

from django.http import HttpResponse
from dmr import Controller
from dmr.plugins.msgspec import MsgspecSerializer

from geo_polygons.domain.services import GetPolygonService
from geo_polygons.infrastructure.nominatim import NominatimPolygonService
from geo_polygons.infrastructure.repository import DjangoPolygonRepository
from premium.services.access import has_advanced_premium


def _get_polygon_service() -> GetPolygonService:
    return GetPolygonService(
        repository=DjangoPolygonRepository(),
        external_service=NominatimPolygonService(),
    )


def _safe_geojson_filename(name: str) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name).strip()
    return sanitized or 'osm_object'


class GetOSMPolygonController(Controller[MsgspecSerializer]):
    """
    Presentation layer: принимает HTTP-запрос, делегирует domain service,
    возвращает HTTP-ответ для просмотра полигона на карте.
    """

    def get(self) -> Any:
        if not self.request.user.is_authenticated:
            return self.to_response(
                raw_data={'detail': 'Требуется авторизация'},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        relation_id = self.kwargs['relation_id']

        service = _get_polygon_service()
        polygon = service.execute(relation_id)

        if polygon is None:
            return self.to_response(
                raw_data={'detail': 'Полигон не найден'},
                status_code=HTTPStatus.NOT_FOUND,
            )

        return self.to_response(
            raw_data=polygon.to_geojson_feature(),
        )


class DownloadOSMPolygonController(Controller[MsgspecSerializer]):
    """Скачивание GeoJSON полигона — только для пользователей с расширенной подпиской."""

    def get(self) -> Any:
        if not self.request.user.is_authenticated:
            return self.to_response(
                raw_data={'detail': 'Требуется авторизация'},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        if not has_advanced_premium(self.request.user):
            return self.to_response(
                raw_data={'detail': 'Требуется расширенная подписка для скачивания'},
                status_code=HTTPStatus.FORBIDDEN,
            )

        relation_id = self.kwargs['relation_id']
        polygon = _get_polygon_service().execute(relation_id)

        if polygon is None:
            return self.to_response(
                raw_data={'detail': 'Полигон не найден'},
                status_code=HTTPStatus.NOT_FOUND,
            )

        filename = f'{_safe_geojson_filename(polygon.name)}.geojson'
        content = json.dumps(polygon.to_geojson_feature(), ensure_ascii=False)
        response = HttpResponse(content, content_type='application/geo+json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
