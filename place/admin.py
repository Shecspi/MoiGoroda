from django.contrib import admin

from place.models import TagOSM


@admin.register(TagOSM)
class TagOSMAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)
