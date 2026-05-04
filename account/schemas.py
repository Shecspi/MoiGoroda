from __future__ import annotations

import msgspec


class Quantity(msgspec.Struct):
    count: int


class DailyStatistics(msgspec.Struct):
    label: str
    count: int


class VisitedCitiesCountryCoverage(msgspec.Struct):
    name: str
    visited_cities: int
    total_cities: int
    rank: int
    total_users_count: int


class VisitedCitiesCountryVisits(msgspec.Struct):
    name: str
    visits: int
    rank: int
    total_users_count: int


class VisitedRegionsCountryCoverage(msgspec.Struct):
    name: str
    visited_regions: int
    total_regions: int
    finished_regions: int


class PersonalVisitedCitiesOverviewResponse(msgspec.Struct):
    total_users_count: int
    unique_visited_cities: Quantity
    unique_visited_cities_rank: int
    total_visited_cities_visits: Quantity
    total_visited_cities_visits_rank: int
    new_visited_cities: Quantity
    new_visited_cities_by_year: list[DailyStatistics]
    unique_visited_cities_by_year: list[DailyStatistics]
    total_visited_cities_visits_by_year: list[DailyStatistics]
    total_region_visits: Quantity
    unique_visited_regions: Quantity
    new_visited_regions: Quantity
    total_region_visits_by_year: list[DailyStatistics]
    unique_visited_regions_by_year: list[DailyStatistics]
    new_visited_regions_by_year: list[DailyStatistics]
    new_visited_cities_by_month: list[DailyStatistics]
    unique_visited_cities_by_month: list[DailyStatistics]
    total_visited_cities_visits_by_month: list[DailyStatistics]


class PersonalVisitedCitiesCountriesCoverageResponse(msgspec.Struct):
    countries_coverage: list[VisitedCitiesCountryCoverage]


class PersonalVisitedCitiesCountriesVisitsResponse(msgspec.Struct):
    countries_visits: list[VisitedCitiesCountryVisits]


class PersonalVisitedRegionsCountriesCoverageResponse(msgspec.Struct):
    countries_coverage: list[VisitedRegionsCountryCoverage]


class RegionVisitedCitiesTreemapItem(msgspec.Struct):
    fullname: str
    unique_visited_cities: int
    total_cities: int


class RegionsVisitedCitiesCountryOption(msgspec.Struct):
    code: str
    name: str
    number_of_visited_cities: int
    number_of_cities: int


class RegionsVisitedCitiesCountriesResponse(msgspec.Struct):
    countries: list[RegionsVisitedCitiesCountryOption]


class RegionsVisitedCitiesTreemapResponse(msgspec.Struct):
    items: list[RegionVisitedCitiesTreemapItem]


class VisitedCountriesByLocationItem(msgspec.Struct):
    location_name: str
    visited: int
    total: int


class PersonalVisitedCountriesOverviewResponse(msgspec.Struct):
    visited: int
    total: int
    by_location: list[VisitedCountriesByLocationItem]
