"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib import admin

from country.models import PartOfTheWorld, Country, Location, VisitedCountry

admin.site.register([PartOfTheWorld, Location])


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'fullname', 'code', 'location', 'is_member_of_un', 'owner')
    search_fields = ('name', 'fullname', 'code')


@admin.register(VisitedCountry)
class VisitedCountryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'country',
        'location',
        'part_of_the_world',
        'user',
    )
    ordering = ('country', 'user')

    @admin.display(description='Расположение', ordering='country__location__name')
    def location(self, obj):
        return obj.country.location

    @admin.display(description='Часть света', ordering='country__location__part_of_the_world__name')
    def part_of_the_world(self, obj):
        return obj.country.location.part_of_the_world
