from django.contrib import admin

from .models import *

admin.site.register(Area)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_title', 'area', 'iso3166')

    def get_title(self, object):
        return object
