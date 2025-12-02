"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from account.models import ShareSettings, UserConsent


@admin.register(ShareSettings)
class ShareSettingsAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'user',
        'can_share',
        'can_share_dashboard',
        'can_share_city_map',
        'can_share_region_map',
        'can_subscribe',
    )
    search_fields = ('user__username',)


class CustomUserAdmin(UserAdmin):  # type: ignore[type-arg]
    # Расширяем list_display дополнительными полями
    list_display = tuple(
        list(UserAdmin.list_display)  # type: ignore[misc]
        + ['number_of_total_cities', 'number_of_unique_cities']
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
        """Возвращает queryset пользователей с аннотированными полями статистики"""
        qs = super().get_queryset(request)
        return qs.annotate(  # type: ignore[no-any-return]
            number_of_total_cities=Count('visitedcity'),
            number_of_unique_cities=Count('visitedcity__city', distinct=True),
        )

    def number_of_total_cities(self, obj: User) -> int:
        return obj.number_of_total_cities  # type: ignore[attr-defined,no-any-return]

    def number_of_unique_cities(self, obj: User) -> int:
        return obj.number_of_unique_cities  # type: ignore[attr-defined,no-any-return]

    number_of_total_cities.short_description = 'Всего посещений'  # type: ignore[attr-defined]
    number_of_total_cities.admin_order_field = 'number_of_total_cities'  # type: ignore[attr-defined]
    number_of_unique_cities.short_description = 'Уникальных городов'  # type: ignore[attr-defined]
    number_of_unique_cities.admin_order_field = 'number_of_unique_cities'  # type: ignore[attr-defined]


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'id',
        'user',
        'consent_given',
        'policy_version',
        'consent_timestamp',
        'ip_address',
    )
    search_fields = ('user__username', 'policy_version')
    list_filter = ('consent_given', 'consent_timestamp', 'policy_version')
    readonly_fields = ('consent_timestamp',)
