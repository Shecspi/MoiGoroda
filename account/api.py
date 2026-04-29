from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.db.models.functions import TruncYear
from dmr import Controller
from dmr.plugins.msgspec import MsgspecSerializer

from city.models import VisitedCity
from region.models import Region
from account.schemas import (
    DailyStatistics,
    PersonalVisitedCitiesOverviewResponse,
    Quantity,
    RegionsVisitedCitiesTreemapResponse,
    RegionVisitedCitiesTreemapItem,
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

        return PersonalVisitedCitiesOverviewResponse(
            unique_visited_cities=Quantity(count=unique_total),
            total_visited_cities_visits=Quantity(count=visits_total),
            new_visited_cities_by_year=new_by_year,
            unique_visited_cities_by_year=unique_by_year,
            total_visited_cities_visits_by_year=visits_by_year,
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
