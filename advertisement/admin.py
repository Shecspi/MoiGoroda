from django.contrib import admin

from advertisement.models import LinkAdvertisement, AdvertisementException


@admin.register(LinkAdvertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'legal_marking', 'icon_class', 'color')
    search_fields = ('title',)


@admin.register(AdvertisementException)
class AdvertisementExceptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'deadline')
    search_fields = ('user',)
