from django.contrib import admin

from subscribe.models import Subscribe


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'subscribe_from',
        'subscribe_to',
    )
