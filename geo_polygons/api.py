from __future__ import annotations

from http import HTTPStatus
from typing import Any

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


class GetOSMPolygonController(Controller[MsgspecSerializer]):
    """
    Presentation layer: принимает HTTP-запрос, делегирует domain service,
    возвращает HTTP-ответ.
    """

    def get(self) -> Any:
        if not self.request.user.is_authenticated:
            return self.to_response(
                raw_data={'detail': 'Требуется авторизация'},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        relation_id = self.kwargs['relation_id']
        is_download = self.request.GET.get('download') == '1'

        if is_download:
            if not has_advanced_premium(self.request.user):
                return self.to_response(
                    raw_data={'detail': 'Требуется расширенная подписка для скачивания'},
                    status_code=HTTPStatus.FORBIDDEN,
                )

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
