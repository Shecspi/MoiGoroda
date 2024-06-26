"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib import admin

from .models import City, VisitedCity


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'region',
        'get_area',
        'population',
        'is_wiki_link',
        'date_of_foundation',
        'is_coordinates',
    )
    search_fields = ('title',)
    fieldsets = [
        (None, {'fields': ['title', 'region', 'population', 'date_of_foundation', 'wiki']}),
        ('Координаты', {'fields': ['coordinate_width', 'coordinate_longitude']}),
    ]

    def is_wiki_link(self, obj):
        return bool(obj.wiki)

    def is_coordinates(self, obj):
        return bool(obj.coordinate_width and obj.coordinate_longitude)

    def get_area(self, obj):
        return obj.region.area

    get_area.short_description = 'Федеральный округ'
    is_wiki_link.short_description = 'Ссылка на Wiki'
    is_wiki_link.boolean = True
    is_coordinates.short_description = 'Координаты'
    is_coordinates.boolean = True


@admin.register(VisitedCity)
class VisitedCityAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'region', 'user', 'date_of_visit', 'has_magnet', 'rating')
    list_filter = ('user',)
    search_fields = ('user__username', 'city__title', 'region__title')
