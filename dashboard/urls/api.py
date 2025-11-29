"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import include, path
from django_modern_rest.routing import Router
from dashboard.api import (
    GetNumberOfUsersController,
    GetNumberOfRegistrationsYesterdayController,
    GetNumberOfRegistrationsWeekController,
    GetNumberOfRegistrationsMonthController,
    GetTotalVisitedCitiesVisitsController,
    GetUniqueVisitedCitiesController,
    GetMaxQtyUniqueVisitedCitiesController,
    GetMaxQtyVisitedCitiesController,
    GetNumberOfUsersWithoutVisitedCitiesController,
    GetAverageQtyVisitedCitiesController,
    GetAverageQtyUniqueVisitedCitiesController,
    GetTotalVisitedCountriesController,
    GetUsersWithVisitedCountriesController,
    GetAverageQtyVisitedCountriesController,
    GetAddedVisitedCountryController,
    GetMaxQtyVisitedCountriesController,
    GetAddedVisitedCountriesChartController,
    GetRegistrationsChartController,
    GetVisitedCitiesByUserChartController,
)

router = Router(
    [
        path(
            'users/',
            GetNumberOfUsersController.as_view(),
        ),
        path(
            'users/registrations/yesterday/',
            GetNumberOfRegistrationsYesterdayController.as_view(),
        ),
        path(
            'users/registrations/week/',
            GetNumberOfRegistrationsWeekController.as_view(),
        ),
        path(
            'users/registrations/month/',
            GetNumberOfRegistrationsMonthController.as_view(),
        ),
        path(
            'users/without_visited_cities/',
            GetNumberOfUsersWithoutVisitedCitiesController.as_view(),
        ),
        path(
            'visited_cities/total/',
            GetTotalVisitedCitiesVisitsController.as_view(),
        ),
        path(
            'visited_cities/unique/',
            GetUniqueVisitedCitiesController.as_view(),
        ),
        path(
            'visited_cities/max_unique/',
            GetMaxQtyUniqueVisitedCitiesController.as_view(),
        ),
        path(
            'visited_cities/max/',
            GetMaxQtyVisitedCitiesController.as_view(),
        ),
        path(
            'visited_cities/average/',
            GetAverageQtyVisitedCitiesController.as_view(),
        ),
        path(
            'visited_cities/average_unique/',
            GetAverageQtyUniqueVisitedCitiesController.as_view(),
        ),
        # Страны
        path(
            'visited_countries/total/',
            GetTotalVisitedCountriesController.as_view(),
        ),
        path(
            'visited_countries/users/',
            GetUsersWithVisitedCountriesController.as_view(),
        ),
        path(
            'visited_countries/average/',
            GetAverageQtyVisitedCountriesController.as_view(),
        ),
        path(
            'visited_countries/max/',
            GetMaxQtyVisitedCountriesController.as_view(),
        ),
        path(
            'visited_countries/added/<int:days>/',
            GetAddedVisitedCountryController.as_view(),
        ),
        path(
            'visited_countries/added/chart/',
            GetAddedVisitedCountriesChartController.as_view(),
        ),
        # Графики
        path(
            'users/registrations/chart/',
            GetRegistrationsChartController.as_view(),
        ),
        path(
            'visited_cities/by_user/chart/',
            GetVisitedCitiesByUserChartController.as_view(),
        ),
    ],
)

urlpatterns = [
    path('', include(router.urls)),
]
