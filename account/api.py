from __future__ import annotations

import calendar
import datetime

from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncYear
from dmr import Controller
from dmr.plugins.msgspec import MsgspecSerializer

from city.models import VisitedCity
from country.repository import (
    get_countries_with_visited_city,
    get_list_of_countries_with_visited_regions,
)
from region.models import Region
from account.schemas import (
    DailyStatistics,
    PersonalVisitedCitiesCountriesCoverageResponse,
    PersonalVisitedCitiesOverviewResponse,
    PersonalVisitedRegionsCountriesCoverageResponse,
    Quantity,
    RegionsVisitedCitiesTreemapResponse,
    RegionVisitedCitiesTreemapItem,
    VisitedCitiesCountryCoverage,
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
            unique_visited_cities=Quantity(count=unique_total),
            total_visited_cities_visits=Quantity(count=visits_total),
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

        countries_coverage = [
            VisitedCitiesCountryCoverage(
                name=country.name,
                visited_cities=country.visited_cities,
                total_cities=country.total_cities,
            )
            for country in get_countries_with_visited_city(user.id)
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


class GetRegionsVisitedCitiesTreemapController(Controller[MsgspecSerializer]):
    def get(self) -> RegionsVisitedCitiesTreemapResponse:
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied

        requested_country_code = (self.request.GET.get('country_code') or 'RU').upper()

        regions = (
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

        items = [
            RegionVisitedCitiesTreemapItem(
                fullname=region['full_name'],
                unique_visited_cities=region['unique_visited_cities'],
                total_cities=region['total_cities'],
            )
            for region in regions
        ]

        return RegionsVisitedCitiesTreemapResponse(items=items)
