"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path

from place.api import CreatePlace, DeletePlace, GetPlaces

urlpatterns = [
    path('', GetPlaces.as_view(), name='get_places'),
    path('create/', CreatePlace.as_view(), name='create_place'),
    path('delete/<int:pk>', DeletePlace.as_view(), name='delete_place'),
]
