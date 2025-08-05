"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path

from .views import save, delete_subscriber

urlpatterns = [
    path('save', save, name='save_subscribe'),
    path('subscriber/delete', delete_subscriber, name='delete_subscribe'),
]
