"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path

from country import views

urlpatterns = [
    path('map', views.country, name='country_map'),
]
