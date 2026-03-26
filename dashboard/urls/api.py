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
    GetVisitedCitiesOverviewController,
    GetNumberOfUsersController,
    GetRegistrationsByRangeController,
    GetRegistrationsComparisonController,
    GetRegistrationsCumulativeChartController,
    GetNumberOfUsersWithoutVisitedCitiesController,
    GetVisitedCountriesOverviewController,
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
            'visited_cities/overview/',
            GetVisitedCitiesOverviewController.as_view(),
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
    ],
)

urlpatterns = [
    path('', include(router.urls)),
]
