from django.contrib import admin

from advertisement.models import AdvertisementException


@admin.register(AdvertisementException)
class AdvertisementExceptionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('user', 'deadline')
    search_fields = ('user',)
