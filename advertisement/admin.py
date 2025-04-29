from django.contrib import admin

from advertisement.models import LinkAdvertisement


@admin.register(LinkAdvertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'legal_marking', 'icon_class', 'color')
    search_fields = ('title',)
