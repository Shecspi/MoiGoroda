from django.contrib import admin

from subscribe.infrastructure.models import VisitedCityNotification
from subscribe.models import Subscribe


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'subscribe_from',
        'subscribe_to',
    )


@admin.register(VisitedCityNotification)
class VisitedCityNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'sender', 'city', 'is_read', 'created_at', 'read_at')
