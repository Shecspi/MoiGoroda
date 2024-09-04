"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path

from country import api

urlpatterns = [
    path('all', api.GetAllCountry.as_view(), name='api__get_all_countries'),
    path('visited', api.GetVisitedCountry.as_view(), name='api__get_visited_countries'),
    path('add', api.AddVisitedCountry.as_view(), name='api__add_visited_countries'),
    path(
        'delete/<str:code>',
        api.DeleteVisitedCountry.as_view(),
        name='api__delete_visited_countries',
    ),
    path(
        'unknown_countries',
        api.RecieveUnknownCountries.as_view(),
        name='api__revieve_unknown_countries',
    ),
]
