"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import include
from dmr.routing import Router, path
from dashboard.api import (
    GetBlogArticlesOverviewController,
    GetPersonalCollectionsOverviewController,
    GetPlacesOverviewController,
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
    GetVisitedCountriesOverviewController,
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
            'visited_countries/overview/',
            GetVisitedCountriesOverviewController.as_view(),
        ),
        # Места
        path(
            'places/overview/',
            GetPlacesOverviewController.as_view(),
        ),
        path(
            'places/personal_collections/overview/',
            GetPersonalCollectionsOverviewController.as_view(),
        ),
        # Блог
        path(
            'blog/articles/overview/',
            GetBlogArticlesOverviewController.as_view(),
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
