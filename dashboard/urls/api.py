"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import include, path
from dashboard.api import (
    GetTotalVisitedCountries,
    GetUsersWithVisitedCountries,
    GetAverageQtyVisitedCountries,
    GetAddedVisitedCountryYeterday,
    GetMaxQtyVisitedCountries,
    GetAddedVisitedCountriesByDay,
)


from django_modern_rest.routing import Router
from dashboard.api import (
    GetNumberOfUsersController,
    GetNumberOfRegistrationsYesterdayController,
    GetNumberOfRegistrationsWeekController,
    GetNumberOfRegistrationsMonthController,
)

router = Router(
    [
        path(
            'get_number_of_users/',
            GetNumberOfUsersController.as_view(),
        ),
        path(
            'get_number_of_registrations_yesterday/',
            GetNumberOfRegistrationsYesterdayController.as_view(),
        ),
        path(
            'get_number_of_registrations_week/',
            GetNumberOfRegistrationsWeekController.as_view(),
        ),
        path(
            'get_number_of_registrations_month/',
            GetNumberOfRegistrationsMonthController.as_view(),
        ),
    ],
)

urlpatterns = [
    path('', include(router.urls)),
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
    path(
        'get_added_visited_countries_by_day',
        GetAddedVisitedCountriesByDay.as_view(),
        name='api__get_added_visited_countries_by_day',
    ),
]
