"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import TYPE_CHECKING

from django.contrib import admin

from collection.models import Collection, FavoriteCollection

if TYPE_CHECKING:
    pass


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Админ-панель для модели Collection."""

    list_display = ('title', 'get_cities_count')
    search_fields = ('title',)

    def get_cities_count(self, obj: Collection) -> int:
        """Возвращает количество городов в коллекции."""
        return obj.city.count()

    get_cities_count.short_description = 'Количество городов'  # type: ignore[attr-defined]


@admin.register(FavoriteCollection)
class FavoriteCollectionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Админ-панель для модели FavoriteCollection."""

    list_display = ('user', 'collection', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'collection__title')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):  # type: ignore[no-untyped-def]
        """Оптимизирует запросы с помощью select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'collection')
