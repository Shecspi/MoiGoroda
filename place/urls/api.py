"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path

from place.api import CreatePlace

urlpatterns = [
    path('create/', CreatePlace.as_view(), name='create_place'),
]
