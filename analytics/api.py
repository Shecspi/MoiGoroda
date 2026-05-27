from __future__ import annotations

import msgspec
from http import HTTPStatus
from typing import Any, Literal

from dmr import Controller, ResponseSpec, modify
from dmr.plugins.msgspec import MsgspecSerializer

from analytics.models import ModeSwitchLog

DisplayMode = Literal['markers', 'polygons']


class ModeSwitchLogBody(msgspec.Struct):
    """Тело запроса на переключение режима отображения."""

    region_slug: str
    mode_from: DisplayMode
    mode_to: DisplayMode


class ModeSwitchLogController(Controller[MsgspecSerializer]):
    @modify(
        status_code=HTTPStatus.CREATED,
        extra_responses=[
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.BAD_REQUEST),
        ],
        tags=['Аналитика'],
    )
    def post(self) -> Any:
        try:
            data = msgspec.json.decode(self.request.body, type=ModeSwitchLogBody)
        except (msgspec.ValidationError, msgspec.DecodeError) as exc:
            return self.to_response(
                raw_data={'detail': str(exc)},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        user = self.request.user
        user_for_log: Any = user if user.is_authenticated else None

        ModeSwitchLog.objects.create(
            user=user_for_log,
            region_slug=data.region_slug,
            mode_from=data.mode_from,
            mode_to=data.mode_to,
        )

        return self.to_response(
            raw_data=None,
            status_code=HTTPStatus.CREATED,
        )
