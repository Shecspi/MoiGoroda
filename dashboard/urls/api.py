"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from dashboard.api import (
    GetTotalVisitedCountries,
    GetUsersWithVisitedCountries,
    GetAverageQtyVisitedCountries,
    GetAddedVisitedCountryYeterday,
    GetMaxQtyVisitedCountries,
)

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
    path(
        'get_average_qty_visited_countries',
        GetAverageQtyVisitedCountries.as_view(),
        name='api__get_average_qty_visited_countries',
    ),
    path(
        'get_max_qty_visited_countries',
        GetMaxQtyVisitedCountries.as_view(),
        name='api__max_qty_visited_countries',
    ),
    path(
        'get_qty_of_added_visited_countries_yesterday/<int:days>',
        GetAddedVisitedCountryYeterday.as_view(),
        name='api__get_qty_of_added_visited_countries',
    ),
]
