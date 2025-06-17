"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from admin_auto_filters.filters import AutocompleteFilter

from city.models import City
from django.contrib import admin

from .models import Area, Region


class RegionFilter(AutocompleteFilter):
    title = 'Страна'
    field_name = 'country'


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_qty_of_regions', 'get_qty_of_cities')

    def get_qty_of_regions(self, area):
        return Region.objects.filter(area=area).count()

    def get_qty_of_cities(self, area):
        return City.objects.filter(region__area=area).count()

    get_qty_of_regions.short_description = 'Количество регионов'
    get_qty_of_cities.short_description = 'Количество городов'


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    fields = ['country', 'area', 'title', 'type', 'full_name', 'iso3166']
    list_display = ('id', 'get_title', 'get_qty_of_cities', 'country', 'area', 'iso3166')
    search_fields = ('title',)
    list_filter = (RegionFilter,)

    def get_title(self, region):
        return region

    def get_qty_of_cities(self, region):
        return City.objects.filter(region=region).count()

    get_title.short_description = 'Название'
    get_qty_of_cities.short_description = 'Количество городов'
