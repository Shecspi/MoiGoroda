# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""DMR справочники стран и городов для каскадного выбора города."""

from __future__ import annotations

from http import HTTPStatus
from typing import Annotated, Any

import msgspec
from dmr import Controller, Query, ResponseSpec, modify
from dmr.plugins.msgspec import MsgspecSerializer

from city.models import City
from country.models import Country
from city.services.search import CitySearchService

SearchText = Annotated[str, msgspec.Meta(min_length=1, max_length=100)]
CountryCode = Annotated[str, msgspec.Meta(min_length=2, max_length=2)]
RegionCode = Annotated[str, msgspec.Meta(min_length=1, max_length=10)]
SearchLimit = Annotated[int, msgspec.Meta(ge=1, le=200)]


class CitySearchQuery(msgspec.Struct, kw_only=True, forbid_unknown_fields=True):
    query: SearchText
    country: CountryCode | None = None
    region: RegionCode | None = None
    limit: SearchLimit = 50


class CitySearchItem(msgspec.Struct):
    id: int
    title: str
    region: str | None
    country: str | None
    country_code: str | None
    region_code: str | None


def _city_data(city: City, *, include_country: bool) -> dict[str, Any]:
    region = city.region
    return {
        'id': city.id,
        'title': city.title,
        'region': region.full_name if region is not None else None,
        'country': city.country.name if include_country else None,
    }


class CityListByRegionController(Controller[MsgspecSerializer]):
    """Возвращает города региона в прежнем response формате."""

    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[ResponseSpec(dict[str, str], status_code=HTTPStatus.BAD_REQUEST)],
        tags=['Города'],
    )
    def get(self) -> Any:
        region_id = self.request.GET.get('region_id')
        if not region_id:
            return self.to_response(
                raw_data={'detail': 'Параметр region_id является обязательным'},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        cities = (
            City.objects.filter(region_id=region_id)
            .select_related('region', 'country')
            .order_by('title')
        )
        return self.to_response(
            raw_data=[_city_data(city, include_country=True) for city in cities],
            status_code=HTTPStatus.OK,
        )


class CityListByCountryController(Controller[MsgspecSerializer]):
    """Возвращает города страны в прежнем response формате."""

    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[ResponseSpec(dict[str, str], status_code=HTTPStatus.BAD_REQUEST)],
        tags=['Города'],
    )
    def get(self) -> Any:
        country_id = self.request.GET.get('country_id')
        if not country_id:
            return self.to_response(
                raw_data={'detail': 'Параметр country_id является обязательным'},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        cities = (
            City.objects.filter(country_id=country_id)
            .select_related('region', 'country')
            .order_by('title')
        )
        return self.to_response(
            raw_data=[_city_data(city, include_country=False) for city in cities],
            status_code=HTTPStatus.OK,
        )


class CityCountryListController(Controller[MsgspecSerializer]):
    """Возвращает страны с городами в прежнем формате city API."""

    @modify(
        status_code=HTTPStatus.OK,
        tags=['Страны'],
    )
    def get(self) -> Any:
        countries = Country.objects.filter(city__isnull=False).distinct().order_by('name')
        return self.to_response(
            raw_data=[
                {'id': country.id, 'code': country.code, 'name': country.name}
                for country in countries
            ],
            status_code=HTTPStatus.OK,
        )


class CitySearchController(
    Query[CitySearchQuery],
    Controller[MsgspecSerializer],
):
    """Ищет города по названию и ISO-кодам страны или региона."""

    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(
                dict[str, list[dict[str, str]]],
                status_code=HTTPStatus.BAD_REQUEST,
            ),
        ],
        tags=['Города'],
    )
    def get(self) -> Any:
        params = self.parsed_query
        query = params.query.strip()
        if not query:
            return self.to_response(
                raw_data={'detail': [{'msg': 'Параметр query не должен быть пустым'}]},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        country = params.country.strip() if params.country is not None else None
        if params.country is not None and (not country or len(country) != 2):
            return self.to_response(
                raw_data={'detail': [{'msg': 'Параметр country должен содержать два символа'}]},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        region = params.region.strip() if params.region is not None else None
        if params.region is not None and (not region or len(region) > 10):
            return self.to_response(
                raw_data={
                    'detail': [{'msg': 'Параметр region должен содержать от 1 до 10 символов'}]
                },
                status_code=HTTPStatus.BAD_REQUEST,
            )

        cities = CitySearchService.search_cities(
            query=query,
            country=country,
            region=region,
            limit=params.limit,
        )

        return self.to_response(
            raw_data=[
                CitySearchItem(
                    id=city.id,
                    title=city.title,
                    region=city.region.full_name if city.region is not None else None,
                    country=(
                        None
                        if country is not None
                        else city.country.name
                        if city.country is not None
                        else None
                    ),
                    country_code=city.country.code if city.country is not None else None,
                    region_code=city.region.iso3166 if city.region is not None else None,
                )
                for city in cities
            ],
            status_code=HTTPStatus.OK,
        )
