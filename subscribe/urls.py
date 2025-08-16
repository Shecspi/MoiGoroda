"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from subscribe.api.dependencies import get_notification_service
from subscribe.api.views import NotificationViewSet
from subscribe.views import (
    save,
    delete_subscriber,
)


class InjectedNotificationViewSet(NotificationViewSet):
    service_class = staticmethod(get_notification_service)


router = DefaultRouter()
router.register(r'notification', InjectedNotificationViewSet, basename='notification')


urlpatterns = [
    path('save', save, name='save_subscribe'),
    path('subscriber/delete', delete_subscriber, name='delete_subscribe'),
    path('', include(router.urls)),
]
