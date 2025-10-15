"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


from admin_auto_filters.filters import AutocompleteFilter  # type: ignore[import-untyped]
from django.contrib import admin

from city.models import City
from .models import Area, Region, RegionType


class RegionFilter(AutocompleteFilter):  # type: ignore[misc]
    title = 'Страна'
    field_name = 'country'


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('title', 'get_qty_of_regions', 'get_qty_of_cities')

    def get_qty_of_regions(self, area: Area) -> int:
        return Region.objects.filter(area=area).count()

    def get_qty_of_cities(self, area: Area) -> int:
        return City.objects.filter(region__area=area).count()

    get_qty_of_regions.short_description = 'Количество регионов'  # type: ignore[attr-defined]
    get_qty_of_cities.short_description = 'Количество городов'  # type: ignore[attr-defined]


@admin.register(RegionType)
class RegionTypeAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    fields = ('title',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    fields = ['country', 'area', 'title', 'type', 'full_name', 'iso3166']
    list_display = ('id', 'get_title', 'get_qty_of_cities', 'country', 'area', 'iso3166')
    search_fields = ('title',)
    list_filter = (RegionFilter,)

    def get_title(self, region: Region) -> Region:
        return region

    def get_qty_of_cities(self, region: Region) -> int:
        return City.objects.filter(region=region).count()

    get_title.short_description = 'Название'  # type: ignore[attr-defined]
    get_qty_of_cities.short_description = 'Количество городов'  # type: ignore[attr-defined]
