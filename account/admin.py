"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Count

from account.models import ShareSettings


@admin.register(ShareSettings)
class ShareSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'can_share',
        'can_share_dashboard',
        'can_share_city_map',
        'can_share_region_map',
        'can_subscribe',
    )
    search_fields = ('user__username',)


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('number_of_total_cities', 'number_of_unique_cities')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            number_of_total_cities=Count('visitedcity'),
            number_of_unique_cities=Count('visitedcity__city', distinct=True),
        )

    def number_of_total_cities(self, obj):
        return obj.number_of_total_cities

    def number_of_unique_cities(self, obj):
        return obj.number_of_unique_cities

    number_of_total_cities.short_description = 'Всего посещений'
    number_of_total_cities.admin_order_field = 'number_of_total_cities'
    number_of_unique_cities.short_description = 'Уникальных городов'
    number_of_unique_cities.admin_order_field = 'number_of_unique_cities'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Перемещаем модель в админке в другую группу
ShareSettings._meta.app_label = 'auth'
