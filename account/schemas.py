from __future__ import annotations

import msgspec


class Quantity(msgspec.Struct):
    count: int


class DailyStatistics(msgspec.Struct):
    label: str
    count: int


class PersonalVisitedCitiesOverviewResponse(msgspec.Struct):
    unique_visited_cities: Quantity
    total_visited_cities_visits: Quantity
    new_visited_cities_by_year: list[DailyStatistics]
    unique_visited_cities_by_year: list[DailyStatistics]
    total_visited_cities_visits_by_year: list[DailyStatistics]


class RegionVisitedCitiesTreemapItem(msgspec.Struct):
    fullname: str
    unique_visited_cities: int
    total_cities: int


class RegionsVisitedCitiesTreemapResponse(msgspec.Struct):
    items: list[RegionVisitedCitiesTreemapItem]
