from __future__ import annotations

import calendar
import datetime

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncYear
from dmr import Controller
from dmr.plugins.msgspec import MsgspecSerializer

from city.models import City
from city.models import VisitedCity
from country.models import Country
from country.repository import (
    get_countries_with_visited_city,
    get_list_of_countries_with_visited_regions,
)
from region.models import Region
from account.schemas import (
    DailyStatistics,
    PersonalVisitedCitiesCountriesCoverageResponse,
    PersonalVisitedCitiesCountriesVisitsResponse,
    PersonalVisitedCitiesOverviewResponse,
    PersonalVisitedRegionsCountriesCoverageResponse,
    Quantity,
    RegionsVisitedCitiesTreemapResponse,
    RegionVisitedCitiesTreemapItem,
    VisitedCitiesCountryCoverage,
    VisitedCitiesCountryVisits,
    VisitedRegionsCountryCoverage,
)


class GetPersonalVisitedCitiesOverviewController(Controller[MsgspecSerializer]):
    def get(self) -> PersonalVisitedCitiesOverviewResponse:
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied

        visited_cities_queryset = VisitedCity.objects.filter(user_id=user.id)

        unique_total = visited_cities_queryset.filter(is_first_visit=True).count()
        visits_total = visited_cities_queryset.count()
        total_users_count = User.objects.count()
        users_with_more_unique_visited_cities = (
            VisitedCity.objects.values('user_id')
            .annotate(unique_visited_cities=Count('city_id', distinct=True))
            .filter(unique_visited_cities__gt=unique_total)
            .count()
        )
        unique_visited_cities_rank = users_with_more_unique_visited_cities + 1
        users_with_more_total_visited_cities_visits = (
            VisitedCity.objects.values('user_id')
            .annotate(total_visited_cities_visits=Count('id'))
            .filter(total_visited_cities_visits__gt=visits_total)
            .count()
        )
        total_visited_cities_visits_rank = users_with_more_total_visited_cities_visits + 1

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
            new_visited_cities_by_year=new_by_year,
            unique_visited_cities_by_year=unique_by_year,
            total_visited_cities_visits_by_year=visits_by_year,
            new_visited_cities_by_month=new_by_month,
            unique_visited_cities_by_month=unique_by_month,
            total_visited_cities_visits_by_month=visits_by_month,
        )


class GetPersonalVisitedCitiesCountriesCoverageController(Controller[MsgspecSerializer]):
    def get(self) -> PersonalVisitedCitiesCountriesCoverageResponse:
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied

        countries = list(get_countries_with_visited_city(user.id))
        country_ids = [country.pk for country in countries]
        total_users_count = User.objects.count()
        rank_by_country_id: dict[int, int] = {}

        if country_ids:
            country_users_stats = (
                VisitedCity.objects.filter(is_first_visit=True, city__country_id__in=country_ids)
                .values('city__country_id', 'user_id')
                .annotate(unique_visited_cities=Count('city_id', distinct=True))
            )
            unique_counts_by_country_id: dict[int, list[int]] = {}
            for item in country_users_stats:
                country_id = int(item['city__country_id'])
                unique_counts_by_country_id.setdefault(country_id, []).append(
                    int(item['unique_visited_cities'])
                )

            for country in countries:
                country_id = int(country.pk)
                user_unique_visited_cities = int(country.visited_cities)
                users_with_more_visited_cities = sum(
                    1
                    for unique_count in unique_counts_by_country_id.get(country_id, [])
                    if unique_count > user_unique_visited_cities
                )
                rank_by_country_id[country_id] = users_with_more_visited_cities + 1

        countries_coverage = [
            VisitedCitiesCountryCoverage(
                name=country.name,
                visited_cities=country.visited_cities,
                total_cities=country.total_cities,
                rank=rank_by_country_id.get(int(country.pk), 1),
                total_users_count=total_users_count,
            )
            for country in countries
        ]

        return PersonalVisitedCitiesCountriesCoverageResponse(
            countries_coverage=countries_coverage
        )


class GetPersonalVisitedRegionsCountriesCoverageController(Controller[MsgspecSerializer]):
    def get(self) -> PersonalVisitedRegionsCountriesCoverageResponse:
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied

        countries_coverage = [
            VisitedRegionsCountryCoverage(
                name=country.name,
                visited_regions=country.number_of_visited_regions,
                total_regions=country.number_of_regions,
            )
            for country in get_list_of_countries_with_visited_regions(user.id)
        ]

        return PersonalVisitedRegionsCountriesCoverageResponse(
            countries_coverage=countries_coverage
        )


class GetPersonalVisitedCitiesCountriesVisitsController(Controller[MsgspecSerializer]):
    def get(self) -> PersonalVisitedCitiesCountriesVisitsResponse:
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied

        countries_visits_queryset = (
            VisitedCity.objects.filter(user_id=user.id)
            .values('city__country_id', 'city__country__name')
            .annotate(visits=Count('id'))
            .order_by('-visits', 'city__country__name')
        )
        total_users_count = User.objects.count()
        country_ids = [int(item['city__country_id']) for item in countries_visits_queryset]
        rank_by_country_id: dict[int, int] = {}

        if country_ids:
            country_users_stats = (
                VisitedCity.objects.filter(city__country_id__in=country_ids)
                .values('city__country_id', 'user_id')
                .annotate(visits=Count('id'))
            )
            visits_by_country_id: dict[int, list[int]] = {}
            for item in country_users_stats:
                country_id = int(item['city__country_id'])
                visits_by_country_id.setdefault(country_id, []).append(int(item['visits']))

            for country in countries_visits_queryset:
                country_id = int(country['city__country_id'])
                user_visits = int(country['visits'])
                users_with_more_visits = sum(
                    1
                    for visits in visits_by_country_id.get(country_id, [])
                    if visits > user_visits
                )
                rank_by_country_id[country_id] = users_with_more_visits + 1

        countries_visits = [
            VisitedCitiesCountryVisits(
                name=str(country['city__country__name']),
                visits=int(country['visits']),
                rank=rank_by_country_id.get(int(country['city__country_id']), 1),
                total_users_count=total_users_count,
            )
            for country in countries_visits_queryset
        ]

        return PersonalVisitedCitiesCountriesVisitsResponse(countries_visits=countries_visits)


class GetRegionsVisitedCitiesTreemapController(Controller[MsgspecSerializer]):
    def get(self) -> RegionsVisitedCitiesTreemapResponse:
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied

        requested_country_code = (self.request.GET.get('country_code') or 'RU').upper()

        regions_queryset = (
            Region.objects.filter(country__code=requested_country_code)
            .annotate(
                total_cities=Count('city', distinct=True),
                unique_visited_cities=Count(
                    'city',
                    filter=Q(city__visitedcity__user_id=user.id),
                    distinct=True,
                ),
            )
            .filter(total_cities__gt=0)
            .order_by('-unique_visited_cities', 'full_name')
            .values('full_name', 'unique_visited_cities', 'total_cities')
        )
        regions = list(regions_queryset)

        if not regions:
            country_name = Country.objects.filter(code=requested_country_code).values_list(
                'name', flat=True
            ).first()

            if not country_name:
                country_name = requested_country_code
                
            total_cities = City.objects.filter(country__code=requested_country_code).count()
            unique_visited_cities = (
                VisitedCity.objects.filter(
                    user_id=user.id,
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
