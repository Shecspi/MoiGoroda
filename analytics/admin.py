from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin

from analytics.models import ModeSwitchLog, VisitedCityAddSource

if TYPE_CHECKING:
    BaseVisitedCityAddSourceAdmin = admin.ModelAdmin[VisitedCityAddSource]
    BaseModeSwitchLogAdmin = admin.ModelAdmin[ModeSwitchLog]
else:
    BaseVisitedCityAddSourceAdmin = admin.ModelAdmin
    BaseModeSwitchLogAdmin = admin.ModelAdmin


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


@admin.register(ModeSwitchLog)
class ModeSwitchLogAdmin(BaseModeSwitchLogAdmin):
    list_display = ('user', 'region_slug', 'mode_from', 'mode_to', 'created_at')
    list_filter = ('region_slug', 'mode_from', 'mode_to', 'created_at')
    readonly_fields = ('user', 'region_slug', 'mode_from', 'mode_to', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(self, request: object, obj: object | None = None) -> bool:
        return False
