"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from country.models import PartOfTheWorld, Country, Location, VisitedCountry

admin.site.register([PartOfTheWorld, Location])


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('id', 'name', 'fullname', 'code', 'location', 'is_member_of_un', 'owner')
    search_fields = ('name', 'fullname', 'code')

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet[Country], search_term: str
    ) -> tuple[QuerySet[Country], bool]:
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if request.GET.get('app_label') == 'city' and request.GET.get('field_name') == 'country':
            queryset = queryset.filter(city__isnull=False).distinct()
            use_distinct = True
        return queryset, use_distinct


@admin.register(VisitedCountry)
class VisitedCountryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'id',
        'country',
        'location',
        'part_of_the_world',
        'user',
    )
    ordering = ('country', 'user')

    @admin.display(description='Расположение', ordering='country__location__name')
    def location(self, obj: VisitedCountry) -> Location | None:
        return obj.country.location

    @admin.display(description='Часть света', ordering='country__location__part_of_the_world__name')
    def part_of_the_world(self, obj: VisitedCountry) -> PartOfTheWorld | None:
        return obj.country.location.part_of_the_world if obj.country.location else None
