from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin

from analytics.models import VisitedCityAddSource

if TYPE_CHECKING:
    BaseVisitedCityAddSourceAdmin = admin.ModelAdmin[VisitedCityAddSource]
else:
    BaseVisitedCityAddSourceAdmin = admin.ModelAdmin


@admin.register(VisitedCityAddSource)
class VisitedCityAddSourceAdmin(BaseVisitedCityAddSourceAdmin):
    list_display = ('visited_city_id', 'surface', 'recorded_at', 'raw_hint')
    list_filter = ('surface', 'recorded_at')
    readonly_fields = ('visited_city', 'surface', 'raw_hint', 'recorded_at')
    ordering = ('-recorded_at',)

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(self, request: object, obj: object | None = None) -> bool:
        return False
