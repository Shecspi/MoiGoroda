"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Count

from .models import City, VisitedCity


class HasImageFilter(SimpleListFilter):
    title = 'Фотография'
    parameter_name = 'has_image'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'С фотографией'),
            ('no', 'Без фотографии'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.exclude(image__isnull=True).exclude(image__exact='')
        if value == 'no':
            return queryset.filter(image__isnull=True) | queryset.filter(image__exact='')
        return queryset


class HasWikiLinkFilter(SimpleListFilter):
    title = 'Ссылка на Wikipedia'
    parameter_name = 'has_wiki_link'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'С ссылкой'),
            ('no', 'Без ссылки'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.exclude(wiki__isnull=True).exclude(wiki__exact='')
        if value == 'no':
            return queryset.filter(wiki__isnull=True) | queryset.filter(wiki__exact='')
        return queryset


class HasCoordinatesFilter(SimpleListFilter):
    title = 'Координаты'
    parameter_name = 'has_coordinates'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'С координатами'),
            ('no', 'Без координат'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.exclude(coordinate_width=0).exclude(coordinate_longitude=0)
        if value == 'no':
            return queryset.filter(Q(coordinate_width=0) | Q(coordinate_longitude=0))
        return queryset


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'country',
        'region',
        'number_visits',
        'population',
        'is_wiki_link',
        'date_of_foundation',
        'is_coordinates',
        'exists_image',
    )
    search_fields = ('title',)
    list_filter = (HasImageFilter, HasCoordinatesFilter, HasWikiLinkFilter)
    fieldsets = [
        (
            None,
            {'fields': ['title', 'country', 'region', 'population', 'date_of_foundation', 'wiki']},
        ),
        ('Изображение', {'fields': ['image', 'image_source_text', 'image_source_link']}),
        ('Координаты', {'fields': ['coordinate_width', 'coordinate_longitude']}),
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(visits_count=Count('visitedcity'))

    def is_wiki_link(self, obj):
        return bool(obj.wiki)

    def is_coordinates(self, obj):
        return bool(obj.coordinate_width and obj.coordinate_longitude)

    def exists_image(self, obj):
        return bool(obj.image)

    def number_visits(self, obj):
        return obj.visits_count

    is_wiki_link.short_description = 'Ссылка на Wiki'
    is_wiki_link.boolean = True
    is_coordinates.short_description = 'Координаты'
    is_coordinates.boolean = True
    exists_image.short_description = 'Фотография'
    exists_image.boolean = True
    exists_image.admin_order_field = 'image'
    number_visits.short_description = 'Кол-во посещений'
    number_visits.admin_order_field = 'visits_count'


class UserFilter(AutocompleteFilter):
    title = 'Пользователь'
    field_name = 'user'


@admin.register(VisitedCity)
class VisitedCityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'city',
        'user',
        'date_of_visit',
        'is_first_visit',
        'has_magnet',
        'rating',
    )
    list_filter = (UserFilter,)
    search_fields = ('user__username', 'city__title')
