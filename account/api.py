from __future__ import annotations

import calendar
import datetime
from collections import defaultdict
from typing import Protocol, cast

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count, F, Min, Q
from django.db.models.functions import TruncMonth, TruncYear
from dmr import Controller
from dmr.plugins.msgspec import MsgspecSerializer

from account.models import ShareSettings
from account.schemas import (
    DailyStatistics,
    PersonalVisitedCitiesCountriesCoverageResponse,
    PersonalVisitedCitiesCountriesVisitsResponse,
    PersonalVisitedCitiesOverviewResponse,
    PersonalVisitedCountriesOverviewResponse,
    PersonalVisitedRegionsCountriesCoverageResponse,
    Quantity,
    RegionsVisitedCitiesCountriesResponse,
    RegionsVisitedCitiesTreemapResponse,
    RegionsVisitedCitiesCountryOption,
    RegionVisitedCitiesTreemapItem,
    VisitedCitiesCountryCoverage,
    VisitedCitiesCountryVisits,
    VisitedCountriesByLocationItem,
    VisitedRegionsCountryCoverage,
)
from city.models import City, VisitedCity
from country.models import Country, PartOfTheWorld, VisitedCountry
from country.repository import (
    get_countries_with_visited_city,
    get_list_of_countries_with_visited_regions,
)
from region.models import Region
from region.services.db import get_all_region_with_visited_cities


class CountryWithVisitedCityCounts(Protocol):
    """Подмена типа для `Country`, аннотированного в `get_countries_with_visited_city`."""

    pk: int
    name: str
    visited_cities: int
    total_cities: int


class CountryWithVisitedRegionsCounts(Protocol):
    """Подмена типа для `Country` из `get_list_of_countries_with_visited_regions`."""

    name: str
    number_of_visited_regions: int
    number_of_regions: int


def resolve_statistics_user_id(request_user: object, shared_user_id_raw: str | None) -> int:
    if shared_user_id_raw:
        try:
            shared_user_id = int(shared_user_id_raw)
        except (TypeError, ValueError):
            raise PermissionDenied

        if shared_user_id <= 0:
            raise PermissionDenied

        if not ShareSettings.objects.filter(
            user_id=shared_user_id,
            can_share=True,
            can_share_dashboard=True,
        ).exists():
            raise PermissionDenied

        return shared_user_id

    if not getattr(request_user, 'is_authenticated', False):
        raise PermissionDenied

    user_id = getattr(request_user, 'id', None)
    if not user_id:
        raise PermissionDenied

    return int(user_id)


TREEMAP_COUNTRY_CODE_MAX_LEN = 3  # ISO alpha-2 или alpha-3
TREEMAP_COUNTRY_CODE_RAW_MAX_SCAN = 32  # лимит прохода по сырой строке из query


def normalize_treemap_country_code(raw: str | None) -> str:
    """
    Из query: только латинские буквы с начала значения до первого иного символа,
    не больше TREEMAP_COUNTRY_CODE_MAX_LEN; пустое — код по умолчанию RU.
    """
    if raw is None:
        return 'RU'
    chars: list[str] = []
    for ch in raw.strip()[:TREEMAP_COUNTRY_CODE_RAW_MAX_SCAN].upper():
        oc = ord(ch)
        if ord('A') <= oc <= ord('Z'):
            chars.append(ch)
            if len(chars) >= TREEMAP_COUNTRY_CODE_MAX_LEN:
                break
        else:
            break
    return ''.join(chars) if chars else 'RU'


def get_unique_visited_cities_country_rank(country_id: int, user_unique_visited_cities: int) -> int:
    users_with_more_visited_cities = (
        VisitedCity.objects.filter(is_first_visit=True, city__country_id=country_id)
        .values('user_id')
        .annotate(unique_visited_cities=Count('city_id', distinct=True))
        .filter(unique_visited_cities__gt=user_unique_visited_cities)
        .count()
    )
    return users_with_more_visited_cities + 1


def get_visited_cities_visits_country_rank(country_id: int, visits: int) -> int:
    users_with_more_visits = (
        VisitedCity.objects.filter(city__country_id=country_id)
        .values('user_id')
        .annotate(visits=Count('id'))
        .filter(visits__gt=visits)
        .count()
    )
    return users_with_more_visits + 1


class GetPersonalVisitedCitiesOverviewController(Controller[MsgspecSerializer]):
    def get(self) -> PersonalVisitedCitiesOverviewResponse:
        user_id = resolve_statistics_user_id(
            self.request.user, self.request.GET.get('shared_user_id')
        )

        visited_cities_queryset = VisitedCity.objects.filter(user_id=user_id)

        unique_total = visited_cities_queryset.filter(is_first_visit=True).count()
        visits_total = visited_cities_queryset.count()
        total_users_count = User.objects.count()
        users_with_more_unique_visited_cities = (
            VisitedCity.objects.values('user_id')
            .annotate(unique_visited_cities=Count('city_id', distinct=True))
            .filter(unique_visited_cities__gt=unique_total)
            .count()
        )
        unique_visited_cities_rank = (
            users_with_more_unique_visited_cities + 1 if unique_total > 0 else 0
        )
        users_with_more_total_visited_cities_visits = (
            VisitedCity.objects.values('user_id')
            .annotate(total_visited_cities_visits=Count('id'))
            .filter(total_visited_cities_visits__gt=visits_total)
            .count()
        )
        total_visited_cities_visits_rank = (
            users_with_more_total_visited_cities_visits + 1 if visits_total > 0 else 0
        )

        unique_by_year_queryset = (
            visited_cities_queryset.annotate(year=TruncYear('date_of_visit'))
            .exclude(year=None)
            .values('year')
            .annotate(qty=Count('city_id', distinct=True))
            .order_by('year')
        )
        visits_by_year_queryset = (
            visited_cities_queryset.annotate(year=TruncYear('date_of_visit'))
            .exclude(year=None)
            .values('year')
            .annotate(qty=Count('id'))
            .order_by('year')
        )
        new_by_year_queryset = (
            visited_cities_queryset.filter(is_first_visit=True)
            .annotate(year=TruncYear('date_of_visit'))
            .exclude(year=None)
            .values('year')
            .annotate(qty=Count('id'))
            .order_by('year')
        )

        unique_by_year = [
            DailyStatistics(label=str(item['year'].year), count=item['qty'])
            for item in unique_by_year_queryset
        ]
        visits_by_year = [
            DailyStatistics(label=str(item['year'].year), count=item['qty'])
            for item in visits_by_year_queryset
        ]
        new_by_year = [
            DailyStatistics(label=str(item['year'].year), count=item['qty'])
            for item in new_by_year_queryset
        ]
        regions_scope_qs = visited_cities_queryset.filter(city__region_id__isnull=False)
        regions_country_raw = self.request.GET.get('regions_country_code')

        if regions_country_raw is not None:
            country_code = normalize_treemap_country_code(regions_country_raw)
            regions_scope_qs = regions_scope_qs.filter(city__country__code=country_code)

        total_region_visits_count = int(regions_scope_qs.count())
        unique_regions_distinct_qs = regions_scope_qs.values('city__region_id').distinct()
        unique_regions_total_count = int(unique_regions_distinct_qs.count())
        new_regions_total_count = unique_regions_total_count

        total_region_visits_by_year_queryset = (
            regions_scope_qs.annotate(year=TruncYear('date_of_visit'))
            .exclude(year=None)
            .values('year')
            .annotate(qty=Count('id'))
            .order_by('year')
        )
        total_region_visits_by_year = [
            DailyStatistics(label=str(item['year'].year), count=item['qty'])
            for item in total_region_visits_by_year_queryset
        ]

        unique_regions_by_year_queryset = (
            regions_scope_qs.annotate(year=TruncYear('date_of_visit'))
            .exclude(year=None)
            .values('year')
            .annotate(qty=Count('city__region_id', distinct=True))
            .order_by('year')
        )
        unique_visited_regions_by_year = [
            DailyStatistics(label=str(item['year'].year), count=item['qty'])
            for item in unique_regions_by_year_queryset
        ]

        new_regions_by_year_map: defaultdict[int, int] = defaultdict(int)
        for row in regions_scope_qs.values('city__region_id').annotate(
            first_visit=Min('date_of_visit')
        ):
            first_visit = row['first_visit']
            if first_visit is None:
                continue
            new_regions_by_year_map[int(first_visit.year)] += 1
        new_visited_regions_by_year = [
            DailyStatistics(label=str(year), count=qty)
            for year, qty in sorted(new_regions_by_year_map.items())
        ]
        now = datetime.datetime.now()
        if now.month == 12:
            month_start = datetime.date(now.year - 1, 1, 1)
        else:
            month_start = datetime.date(now.year - 2, now.month + 1, 1)
        month_end = datetime.date(now.year, now.month, calendar.monthrange(now.year, now.month)[1])

        month_range_queryset = visited_cities_queryset.filter(
            date_of_visit__range=(month_start, month_end)
        )
        unique_by_month_queryset = (
            month_range_queryset.annotate(month=TruncMonth('date_of_visit'))
            .exclude(month=None)
            .values('month')
            .annotate(qty=Count('city_id', distinct=True))
            .order_by('month')
        )
        visits_by_month_queryset = (
            month_range_queryset.annotate(month=TruncMonth('date_of_visit'))
            .exclude(month=None)
            .values('month')
            .annotate(qty=Count('id'))
            .order_by('month')
        )
        new_by_month_queryset = (
            month_range_queryset.filter(is_first_visit=True)
            .annotate(month=TruncMonth('date_of_visit'))
            .exclude(month=None)
            .values('month')
            .annotate(qty=Count('id'))
            .order_by('month')
        )

        unique_by_month = [
            DailyStatistics(label=item['month'].strftime('%m.%Y'), count=item['qty'])
            for item in unique_by_month_queryset
        ]
        visits_by_month = [
            DailyStatistics(label=item['month'].strftime('%m.%Y'), count=item['qty'])
            for item in visits_by_month_queryset
        ]
        new_by_month = [
            DailyStatistics(label=item['month'].strftime('%m.%Y'), count=item['qty'])
            for item in new_by_month_queryset
        ]

        return PersonalVisitedCitiesOverviewResponse(
            total_users_count=total_users_count,
            unique_visited_cities=Quantity(count=unique_total),
            unique_visited_cities_rank=unique_visited_cities_rank,
            total_visited_cities_visits=Quantity(count=visits_total),
            total_visited_cities_visits_rank=total_visited_cities_visits_rank,
            new_visited_cities=Quantity(count=unique_total),
            new_visited_cities_by_year=new_by_year,
            unique_visited_cities_by_year=unique_by_year,
            total_visited_cities_visits_by_year=visits_by_year,
            total_region_visits=Quantity(count=total_region_visits_count),
            unique_visited_regions=Quantity(count=unique_regions_total_count),
            new_visited_regions=Quantity(count=new_regions_total_count),
            total_region_visits_by_year=total_region_visits_by_year,
            unique_visited_regions_by_year=unique_visited_regions_by_year,
            new_visited_regions_by_year=new_visited_regions_by_year,
            new_visited_cities_by_month=new_by_month,
            unique_visited_cities_by_month=unique_by_month,
            total_visited_cities_visits_by_month=visits_by_month,
        )


class GetPersonalVisitedCitiesCountriesCoverageController(Controller[MsgspecSerializer]):
    def get(self) -> PersonalVisitedCitiesCountriesCoverageResponse:
        user_id = resolve_statistics_user_id(
            self.request.user, self.request.GET.get('shared_user_id')
        )

        countries = cast(
            list[CountryWithVisitedCityCounts],
            list(get_countries_with_visited_city(user_id)),
        )
        total_users_count = User.objects.count()

        countries_coverage = [
            VisitedCitiesCountryCoverage(
                name=country.name,
                visited_cities=country.visited_cities,
                total_cities=country.total_cities,
                rank=get_unique_visited_cities_country_rank(
                    country_id=int(country.pk),
                    user_unique_visited_cities=int(country.visited_cities),
                ),
                total_users_count=total_users_count,
            )
            for country in countries
        ]

        return PersonalVisitedCitiesCountriesCoverageResponse(countries_coverage=countries_coverage)


class GetPersonalVisitedRegionsCountriesCoverageController(Controller[MsgspecSerializer]):
    def get(self) -> PersonalVisitedRegionsCountriesCoverageResponse:
        user_id = resolve_statistics_user_id(
            self.request.user, self.request.GET.get('shared_user_id')
        )

        finished_regions_by_country: dict[str, int] = {}
        finished_region_rows = get_all_region_with_visited_cities(user_id).filter(
            num_total=F('num_visited'),
            num_visited__gt=0,
        )  # type: ignore[misc]
        for country_name in finished_region_rows.values_list('country__name', flat=True):
            finished_regions_by_country[country_name] = (
                finished_regions_by_country.get(country_name, 0) + 1
            )

        regions_countries = cast(
            list[CountryWithVisitedRegionsCounts],
            list(get_list_of_countries_with_visited_regions(user_id)),
        )
        countries_coverage = [
            VisitedRegionsCountryCoverage(
                name=country.name,
                visited_regions=country.number_of_visited_regions,
                total_regions=country.number_of_regions,
                finished_regions=finished_regions_by_country.get(country.name, 0),
            )
            for country in regions_countries
        ]

        return PersonalVisitedRegionsCountriesCoverageResponse(
            countries_coverage=countries_coverage
        )


class GetPersonalVisitedCitiesCountriesVisitsController(Controller[MsgspecSerializer]):
    def get(self) -> PersonalVisitedCitiesCountriesVisitsResponse:
        user_id = resolve_statistics_user_id(
            self.request.user, self.request.GET.get('shared_user_id')
        )

        countries_visits_queryset = (
            VisitedCity.objects.filter(user_id=user_id)
            .values('city__country_id', 'city__country__name')
            .annotate(visits=Count('id'))
            .order_by('-visits', 'city__country__name')
        )
        countries_visits = list(countries_visits_queryset)
        total_users_count = User.objects.count()

        country_visits_items = [
            VisitedCitiesCountryVisits(
                name=str(country['city__country__name']),
                visits=int(country['visits']),
                rank=get_visited_cities_visits_country_rank(
                    country_id=int(country['city__country_id']),
                    visits=int(country['visits']),
                ),
                total_users_count=total_users_count,
            )
            for country in countries_visits
        ]

        return PersonalVisitedCitiesCountriesVisitsResponse(countries_visits=country_visits_items)


class GetRegionsVisitedCitiesTreemapController(Controller[MsgspecSerializer]):
    def get(self) -> RegionsVisitedCitiesTreemapResponse:
        user_id = resolve_statistics_user_id(
            self.request.user, self.request.GET.get('shared_user_id')
        )

        requested_country_code = normalize_treemap_country_code(
            self.request.GET.get('country_code')
        )

        regions_queryset = (
            Region.objects.filter(country__code=requested_country_code)
            .annotate(
                total_cities=Count('city', distinct=True),
                unique_visited_cities=Count(
                    'city',
                    filter=Q(city__visitedcity__user_id=user_id),
                    distinct=True,
                ),
            )
            .filter(total_cities__gt=0)
            .order_by('-unique_visited_cities', 'full_name')
            .values('full_name', 'unique_visited_cities', 'total_cities')
        )
        regions = list(regions_queryset)

        if not regions:
            country_name = (
                Country.objects.filter(code=requested_country_code)
                .values_list('name', flat=True)
                .first()
            )

            if not country_name:
                country_name = requested_country_code

            total_cities = City.objects.filter(country__code=requested_country_code).count()
            unique_visited_cities = (
                VisitedCity.objects.filter(
                    user_id=user_id,
                    city__country__code=requested_country_code,
                )
                .values('city_id')
                .distinct()
                .count()
            )
            regions = [
                {
                    'full_name': str(country_name),
                    'unique_visited_cities': unique_visited_cities,
                    'total_cities': total_cities,
                }
            ]

        items = [
            RegionVisitedCitiesTreemapItem(
                fullname=region['full_name'],
                unique_visited_cities=region['unique_visited_cities'],
                total_cities=region['total_cities'],
            )
            for region in regions
        ]

        return RegionsVisitedCitiesTreemapResponse(items=items)


class GetRegionsVisitedCitiesCountriesController(Controller[MsgspecSerializer]):
    def get(self) -> RegionsVisitedCitiesCountriesResponse:
        user_id = resolve_statistics_user_id(
            self.request.user, self.request.GET.get('shared_user_id')
        )

        countries_queryset = (
            Country.objects.filter(city__isnull=False)
            .annotate(
                number_of_visited_cities=Count(
                    'city',
                    filter=Q(city__visitedcity__user_id=user_id),
                    distinct=True,
                ),
                number_of_cities=Count('city', distinct=True),
            )
            .filter(number_of_visited_cities__gt=0)
            .order_by('-number_of_visited_cities', 'name')
            .values('code', 'name', 'number_of_visited_cities', 'number_of_cities')
        )

        countries = [
            RegionsVisitedCitiesCountryOption(
                code=str(country['code']),
                name=str(country['name']),
                number_of_visited_cities=int(country['number_of_visited_cities']),
                number_of_cities=int(country['number_of_cities']),
            )
            for country in countries_queryset
        ]

        return RegionsVisitedCitiesCountriesResponse(countries=countries)


class GetPersonalVisitedCountriesOverviewController(Controller[MsgspecSerializer]):
    def get(self) -> PersonalVisitedCountriesOverviewResponse:
        user_id = resolve_statistics_user_id(
            self.request.user, self.request.GET.get('shared_user_id')
        )

        # Общее количество стран
        total_countries = Country.objects.count()
        visited_countries = VisitedCountry.objects.filter(user_id=user_id).count()

        # По частям света
        parts_of_the_world = PartOfTheWorld.objects.all().order_by('name')
        by_location = []

        for part in parts_of_the_world:
            loc_total = Country.objects.filter(location__part_of_the_world=part).count()

            if loc_total == 0:
                continue

            loc_visited = VisitedCountry.objects.filter(
                user_id=user_id,
                country__location__part_of_the_world=part,
            ).count()
            by_location.append(
                VisitedCountriesByLocationItem(
                    location_name=part.name,
                    visited=loc_visited,
                    total=loc_total,
                )
            )

        return PersonalVisitedCountriesOverviewResponse(
            visited=visited_countries,
            total=total_countries,
            by_location=by_location,
        )
