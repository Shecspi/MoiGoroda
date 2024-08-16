"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path

from country import api

urlpatterns = [
    path('all', api.GetAllCountry.as_view(), name='api__get_all_country'),
]
