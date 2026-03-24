"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import include
from dmr.routing import Router, path
from dashboard.api import (
    GetAddedVisitedCitiesByRangeController,
    GetAddedVisitedCitiesComparisonController,
    GetNumberOfUsersController,
    GetRegistrationsByRangeController,
    GetRegistrationsComparisonController,
    GetRegistrationsCumulativeChartController,
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
    GetVisitedCitiesByUserChartController,
    GetUniqueVisitedCitiesByUserChartController,
)

router = Router(
    'api/dashboard',
    [
        path(
            'users/',
            GetNumberOfUsersController.as_view(),
        ),
        path(
            'users/registrations/range/',
            GetRegistrationsByRangeController.as_view(),
        ),
        path(
            'users/registrations/compare/',
            GetRegistrationsComparisonController.as_view(),
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
        path(
            'visited_cities/added/range/',
            GetAddedVisitedCitiesByRangeController.as_view(),
        ),
        path(
            'visited_cities/added/compare/',
            GetAddedVisitedCitiesComparisonController.as_view(),
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
            'users/registrations/chart/cumulative/',
            GetRegistrationsCumulativeChartController.as_view(),
        ),
        path(
            'visited_cities/by_user/chart/',
            GetVisitedCitiesByUserChartController.as_view(),
        ),
        path(
            'visited_cities/unique_by_user/chart/',
            GetUniqueVisitedCitiesByUserChartController.as_view(),
        ),
    ],
)

urlpatterns = [
    path('', include(router.urls)),
]
