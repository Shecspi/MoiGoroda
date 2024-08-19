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
    path('visited', api.GetVisitedCountry.as_view(), name='api__get_visited_country'),
    path('add', api.AddVisitedCountry.as_view(), name='api__add_visited_country'),
    path('delete', api.DeleteVisitedCountry.as_view(), name='api__delete_visited_country'),
]
