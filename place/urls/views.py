"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path

from place import views

urlpatterns = [
    path('map', views.place, name='place_map'),
]
