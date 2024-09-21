"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from dashboard.api import GetTotalVisitedCountries, GetUsersWithVisitedCountries

urlpatterns = [
    path(
        'get_total_visited_countries',
        GetTotalVisitedCountries.as_view(),
        name='api__get_total_visited_countries',
    ),
    path(
        'get_qty_users_with_visited_countries',
        GetUsersWithVisitedCountries.as_view(),
        name='api__get_qty_users_with_visited_countries',
    ),
]
