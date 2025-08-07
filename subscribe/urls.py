"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    save,
    delete_subscriber,
    NotificationViewSet,
)

urlpatterns = [
    path('save', save, name='save_subscribe'),
    path('subscriber/delete', delete_subscriber, name='delete_subscribe'),
]

router = DefaultRouter()
router.register(r'notification', NotificationViewSet, basename='notification')

urlpatterns += router.urls
