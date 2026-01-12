"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from admin_auto_filters.filters import AutocompleteFilter  # type: ignore[import-untyped]
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Count, QuerySet
from django.http import HttpRequest

from .models import City, CityDistrict, CityListDefaultSettings, VisitedCity, VisitedCityDistrict


class HasImageFilter(SimpleListFilter):
    title = 'Фотография'
    parameter_name = 'has_image'

    def lookups(self, request: HttpRequest, model_admin: Any) -> list[tuple[str, str]]:
        return [
            ('yes', 'С фотографией'),
            ('no', 'Без фотографии'),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet[City]) -> QuerySet[City]:
        value = self.value()
        if value == 'yes':
            return queryset.exclude(image__isnull=True).exclude(image__exact='')
        if value == 'no':
            return queryset.filter(image__isnull=True) | queryset.filter(image__exact='')
        return queryset


class HasWikiLinkFilter(SimpleListFilter):
    title = 'Ссылка на Wikipedia'
    parameter_name = 'has_wiki_link'

    def lookups(self, request: HttpRequest, model_admin: Any) -> list[tuple[str, str]]:
        return [
            ('yes', 'С ссылкой'),
            ('no', 'Без ссылки'),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet[City]) -> QuerySet[City]:
        value = self.value()
        if value == 'yes':
            return queryset.exclude(wiki__isnull=True).exclude(wiki__exact='')
        if value == 'no':
            return queryset.filter(wiki__isnull=True) | queryset.filter(wiki__exact='')
        return queryset


class HasCoordinatesFilter(SimpleListFilter):
    title = 'Координаты'
    parameter_name = 'has_coordinates'

    def lookups(self, request: HttpRequest, model_admin: Any) -> list[tuple[str, str]]:
        return [
            ('yes', 'С координатами'),
            ('no', 'Без координат'),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet[City]) -> QuerySet[City]:
        value = self.value()
        if value == 'yes':
            return queryset.exclude(coordinate_width=0).exclude(coordinate_longitude=0)
        if value == 'no':
            return queryset.filter(Q(coordinate_width=0) | Q(coordinate_longitude=0))
        return queryset


@admin.register(City)
class CityAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
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

    def get_queryset(self, request: HttpRequest) -> QuerySet[City]:
        qs = super().get_queryset(request)
        return qs.annotate(visits_count=Count('visitedcity'))  # type: ignore[no-any-return]

    def is_wiki_link(self, obj: City) -> bool:
        return bool(obj.wiki)

    def is_coordinates(self, obj: City) -> bool:
        return bool(obj.coordinate_width and obj.coordinate_longitude)

    def exists_image(self, obj: City) -> bool:
        return bool(obj.image)

    def number_visits(self, obj: City) -> int:
        return obj.visits_count  # type: ignore[attr-defined,no-any-return]

    is_wiki_link.short_description = 'Ссылка на Wiki'  # type: ignore[attr-defined]
    is_wiki_link.boolean = True  # type: ignore[attr-defined]
    is_coordinates.short_description = 'Координаты'  # type: ignore[attr-defined]
    is_coordinates.boolean = True  # type: ignore[attr-defined]
    exists_image.short_description = 'Фотография'  # type: ignore[attr-defined]
    exists_image.boolean = True  # type: ignore[attr-defined]
    exists_image.admin_order_field = 'image'  # type: ignore[attr-defined]
    number_visits.short_description = 'Кол-во посещений'  # type: ignore[attr-defined]
    number_visits.admin_order_field = 'visits_count'  # type: ignore[attr-defined]


class UserFilter(AutocompleteFilter):  # type: ignore[misc]
    title = 'Пользователь'
    field_name = 'user'


@admin.register(VisitedCity)
class VisitedCityAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'id',
        'city',
        'user',
        'date_of_visit',
        'is_first_visit',
        'has_magnet',
        'rating',
        'created_at',
        'updated_at',
    )
    list_filter = (
        UserFilter,
        'created_at',
        'updated_at',
    )
    search_fields = ('user__username', 'city__title')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(CityListDefaultSettings)
class CityListDefaultSettingsAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'id',
        'user',
        'parameter_type',
        'parameter_value',
    )
    list_filter = (
        'parameter_type',
        UserFilter,
    )
    search_fields = ('user__username', 'parameter_value')
    list_editable = ('parameter_value',)


@admin.register(CityDistrict)
class CityDistrictAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'id',
        'title',
        'city',
        'area',
        'population',
    )
    list_filter = ('city__country', 'city')
    search_fields = ('title', 'city__title')
    autocomplete_fields = ('city',)


@admin.register(VisitedCityDistrict)
class VisitedCityDistrictAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'id',
        'city_district',
        'user',
        'created_at',
        'updated_at',
    )
    list_filter = (
        UserFilter,
        'created_at',
        'updated_at',
    )
    search_fields = ('user__username', 'city_district__title')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('city_district',)
