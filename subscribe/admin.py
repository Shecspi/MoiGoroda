from django.contrib import admin

from subscribe.models import Subscribe, Notification


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'subscribe_from',
        'subscribe_to',
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'sender', 'message', 'is_read', 'created_at', 'read_at')
