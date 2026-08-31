# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""DMR API контроллеры для создания и редактирования посещений городов."""

from __future__ import annotations

from datetime import date
from http import HTTPStatus
from typing import Annotated, Any

import msgspec
from django.contrib.auth.models import User
from dmr import Body, Blueprint, Controller, ResponseSpec, modify
from dmr.plugins.msgspec import MsgspecSerializer
from dmr.response import APIError
from dmr.security.django_session import DjangoSessionSyncAuth
from markdownify.templatetags.markdownify import markdownify  # type: ignore[import-untyped]

from analytics.services import normalize_api_from_raw, record_visited_city_add
from city.models import City, VisitedCity
from city.services.db import (
    get_first_visit_date_by_city,
    get_last_visit_date_by_city,
    get_number_of_users_who_visit_city,
    get_number_of_visits_by_city,
)
from collection.services import get_city_collection_context
from services import logger


Rating = Annotated[int, msgspec.Meta(ge=1, le=5)]
VisitDate = str | None


class RequiredDjangoSessionAuth(DjangoSessionSyncAuth):
    """DMR session auth с совместимым 403 для анонимного create/edit API."""

    def authenticate(self, endpoint: Any, controller: Any) -> Any | None:
        user = super().authenticate(endpoint, controller)
        if user is None:
            raise APIError(
                {'detail': 'Учетные данные не были предоставлены.'},
                status_code=HTTPStatus.FORBIDDEN,
            )
        return user


class AddVisitedCityBody(msgspec.Struct, kw_only=True):
    """Типизированное тело запроса создания посещения."""

    city: int
    rating: Rating
    date_of_visit: VisitDate = None
    has_magnet: bool = False
    impression: str | None = None
    from_page: str | None = msgspec.field(name='from', default=None)


class UpdateVisitedCityBody(msgspec.Struct, kw_only=True):
    """Типизированное тело запроса изменения посещения.

    ``city`` намеренно принимается только для того, чтобы вернуть явную
    validation error вместо молчаливого игнорирования попытки сменить город.
    """

    date_of_visit: VisitDate | msgspec.UnsetType = msgspec.UNSET
    rating: Rating | msgspec.UnsetType = msgspec.UNSET
    has_magnet: bool | msgspec.UnsetType = msgspec.UNSET
    impression: str | None | msgspec.UnsetType = msgspec.UNSET
    city: int | None | msgspec.UnsetType = msgspec.UNSET


def _format_date(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _normalize_visit_date(value: VisitDate) -> date | None:
    """Проверяет ISO-дату и сохраняет совместимость с пустым legacy FormData."""
    if value is None or value == '':
        return None
    return date.fromisoformat(value)


def _visit_payload(visit: VisitedCity) -> dict[str, Any]:
    """Строит данные посещения, нужные форме редактирования и карточке."""
    city = visit.city
    return {
        'id': visit.id,
        'city': city.id,
        'city_title': city.title,
        'region_title': str(city.region) if city.region_id else None,
        'country': city.country.name,
        'date_of_visit': _format_date(visit.date_of_visit),
        'has_magnet': visit.has_magnet,
        'impression': visit.impression,
        'impression_html': ''.join((markdownify(visit.impression),)),
        'rating': visit.rating,
        'lat': str(city.coordinate_width),
        'lon': str(city.coordinate_longitude),
    }


def _city_summary(city: City, user_id: int) -> dict[str, Any]:
    """Строит краткие данные города и статистику, используемую картами."""
    visit_years = [
        value.year
        for value in VisitedCity.objects.filter(
            city=city,
            user_id=user_id,
            date_of_visit__isnull=False,
        ).dates('date_of_visit', 'year')
    ]
    return {
        'id': city.id,
        'name': city.title,
        'title': city.title,
        'region': str(city.region) if city.region_id else None,
        'country': city.country.name,
        'country_code': city.country.code,
        'lat': str(city.coordinate_width),
        'lon': str(city.coordinate_longitude),
        'number_of_visits': get_number_of_visits_by_city(city_id=city.id, user_id=user_id),
        'first_visit_date': _format_date(
            get_first_visit_date_by_city(city_id=city.id, user_id=user_id)
        ),
        'last_visit_date': _format_date(
            get_last_visit_date_by_city(city_id=city.id, user_id=user_id)
        ),
        'visit_years': visit_years,
        'number_of_users_who_visit_city': get_number_of_users_who_visit_city(city_id=city.id),
        'number_of_visits_all_users': VisitedCity.objects.filter(city=city).count(),
    }


class AddVisitedCity(Body[AddVisitedCityBody], Controller[MsgspecSerializer]):
    """Создаёт посещение, сохраняя прежний URL и response contract."""

    csrf_exempt = False
    auth = (RequiredDjangoSessionAuth(),)

    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.BAD_REQUEST),
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.FORBIDDEN),
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.CONFLICT),
        ],
        tags=['Посещённые города'],
    )
    def post(self) -> Any:
        user = self.request.user
        if not user.is_authenticated:
            return self.to_response(
                raw_data={'detail': 'Учетные данные не были предоставлены.'},
                status_code=HTTPStatus.FORBIDDEN,
            )

        assert isinstance(user, User)
        data = self.parsed_body
        from_page = data.from_page or 'unknown location'

        try:
            city = City.objects.select_related('country', 'region').get(pk=data.city)
        except City.DoesNotExist:
            logger.warning(
                self.request,
                f'(API: Add visited city) Unknown city #{data.city} from {from_page}',
            )
            return self.to_response(
                raw_data={'city': ['Выберите корректный город.']},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        try:
            date_of_visit = _normalize_visit_date(data.date_of_visit)
        except ValueError:
            return self.to_response(
                raw_data={'date_of_visit': ['Укажите дату в формате ГГГГ-ММ-ДД.']},
                status_code=HTTPStatus.BAD_REQUEST,
            )
        if VisitedCity.objects.filter(user=user, city=city, date_of_visit=date_of_visit).exists():
            return self.to_response(
                raw_data={
                    'status': 'success',
                    'message': f'Вы уже сохранили посещение города {city} {date_of_visit}',
                },
                status_code=HTTPStatus.CONFLICT,
            )

        collection_context = get_city_collection_context(city)
        is_first_visit = not VisitedCity.objects.filter(user=user, city=city).exists()
        visit = VisitedCity.objects.create(
            user=user,
            city=city,
            date_of_visit=date_of_visit,
            rating=data.rating,
            has_magnet=data.has_magnet,
            impression=data.impression,
            is_first_visit=is_first_visit,
        )

        api_surface, raw_hint = normalize_api_from_raw(data.from_page)
        record_visited_city_add(visited_city=visit, surface=api_surface, raw_hint=raw_hint)
        logger.info(
            self.request,
            f'(API: Add visited city) The visited city has been successfully added from {from_page}',
        )

        visit_data = _visit_payload(visit)
        city_summary = _city_summary(city, user.id)
        city_summary.pop('id')  # ``id`` в legacy create response является ID посещения.
        visit_data.update(city_summary)
        return self.to_response(
            raw_data={
                'status': 'success',
                'city': visit_data,
                'visit': _visit_payload(visit),
                'collection_context': collection_context,
            },
            status_code=HTTPStatus.OK,
        )


def _get_owned_visit(request: Any, visit_id: int) -> VisitedCity | None:
    """Возвращает посещение только если оно принадлежит текущему пользователю."""
    user = request.user
    if not user.is_authenticated:
        return None
    assert isinstance(user, User)
    return (
        VisitedCity.objects.select_related('city__country', 'city__region')
        .filter(pk=visit_id, user=user)
        .first()
    )


def _not_found_response(controller: Any) -> Any:
    """Не раскрывает существование чужих посещений."""
    if not controller.request.user.is_authenticated:
        return controller.to_response(
            raw_data={'detail': 'Учетные данные не были предоставлены.'},
            status_code=HTTPStatus.FORBIDDEN,
        )
    return controller.to_response(
        raw_data={'detail': 'Посещение города не найдено.'},
        status_code=HTTPStatus.NOT_FOUND,
    )


class UpdateVisitedCityBlueprint(Body[UpdateVisitedCityBody], Blueprint[MsgspecSerializer]):
    """PATCH blueprint: Body применяется только к методу, который имеет тело."""

    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.BAD_REQUEST),
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.FORBIDDEN),
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.NOT_FOUND),
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.CONFLICT),
        ],
        tags=['Посещённые города'],
    )
    def patch(self) -> Any:
        visit = _get_owned_visit(self.request, self.kwargs['visit_id'])
        if visit is None:
            return _not_found_response(self)

        data = self.parsed_body
        if data.city is not msgspec.UNSET:
            return self.to_response(
                raw_data={'city': ['Город посещения нельзя изменить.']},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        try:
            requested_date = (
                visit.date_of_visit
                if data.date_of_visit is msgspec.UNSET
                else _normalize_visit_date(data.date_of_visit)
            )
        except ValueError:
            return self.to_response(
                raw_data={'date_of_visit': ['Укажите дату в формате ГГГГ-ММ-ДД.']},
                status_code=HTTPStatus.BAD_REQUEST,
            )
        duplicate_exists = (
            VisitedCity.objects.filter(
                user=visit.user,
                city=visit.city,
                date_of_visit=requested_date,
            )
            .exclude(pk=visit.pk)
            .exists()
        )
        if duplicate_exists:
            return self.to_response(
                raw_data={
                    'status': 'success',
                    'message': f'Вы уже сохранили посещение города {visit.city} {requested_date}',
                },
                status_code=HTTPStatus.CONFLICT,
            )

        visit.date_of_visit = requested_date
        visit.rating = visit.rating if data.rating is msgspec.UNSET else data.rating
        visit.has_magnet = visit.has_magnet if data.has_magnet is msgspec.UNSET else data.has_magnet
        visit.impression = visit.impression if data.impression is msgspec.UNSET else data.impression
        visit.save(
            update_fields=['date_of_visit', 'rating', 'has_magnet', 'impression', 'updated_at']
        )

        assert isinstance(self.request.user, User)
        return self.to_response(
            raw_data={
                'visit': _visit_payload(visit),
                'city': _city_summary(visit.city, self.request.user.id),
            },
            status_code=HTTPStatus.OK,
        )


class VisitedCityDetailController(Controller[MsgspecSerializer]):
    """Возвращает и изменяет только посещение текущего пользователя."""

    blueprints = (UpdateVisitedCityBlueprint,)
    csrf_exempt = False
    auth = (RequiredDjangoSessionAuth(),)

    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.FORBIDDEN),
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.NOT_FOUND),
        ],
        tags=['Посещённые города'],
    )
    def get(self) -> Any:
        visit = _get_owned_visit(self.request, self.kwargs['visit_id'])
        if visit is None:
            return _not_found_response(self)
        assert isinstance(self.request.user, User)
        return self.to_response(
            raw_data={
                'visit': _visit_payload(visit),
                'city': _city_summary(visit.city, self.request.user.id),
            },
            status_code=HTTPStatus.OK,
        )
