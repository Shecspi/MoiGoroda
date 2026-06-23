# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from __future__ import annotations

import msgspec


class NotVisitedCityItem(msgspec.Struct):
    id: int
    title: str
    region: str | None
    region_id: int | None
    country: str
    country_code: str
    lat: str
    lon: str


class NeighboringCityItem(msgspec.Struct):
    id: int
    title: str
    visits: int
    rank: int


class CityStatisticsResponse(msgspec.Struct):
    number_of_cities_in_country: int
    number_of_cities_in_region: int
    rank_in_country_by_visits: int
    rank_in_country_by_users: int
    rank_in_region_by_visits: int
    rank_in_region_by_users: int
    neighboring_cities_by_rank_in_country_by_users: list[NeighboringCityItem]
    neighboring_cities_by_rank_in_country_by_visits: list[NeighboringCityItem]
    neighboring_cities_by_rank_in_region_by_users: list[NeighboringCityItem]
    neighboring_cities_by_rank_in_region_by_visits: list[NeighboringCityItem]
