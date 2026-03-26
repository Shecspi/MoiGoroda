from typing import Any, cast

import pytest
from django.urls import resolve

from dashboard.api import (
    GetBlogArticlesOverviewController,
    GetPersonalCollectionsOverviewController,
    GetPlacesOverviewController,
    GetUsersOverviewController,
    GetVisitedCitiesOverviewController,
    GetVisitedCountriesOverviewController,
)


@pytest.mark.unit
def test_dashboard_api_controllers_importable() -> None:
    controllers = [
        GetUsersOverviewController,
        GetVisitedCitiesOverviewController,
        GetVisitedCountriesOverviewController,
        GetPlacesOverviewController,
        GetPersonalCollectionsOverviewController,
        GetBlogArticlesOverviewController,
    ]
    assert all(controller is not None for controller in controllers)


@pytest.mark.unit
@pytest.mark.parametrize(
    ('path', 'controller_name'),
    [
        ('/api/dashboard/users/overview/', 'GetUsersOverviewController'),
        ('/api/dashboard/visited_cities/overview/', 'GetVisitedCitiesOverviewController'),
        ('/api/dashboard/visited_countries/overview/', 'GetVisitedCountriesOverviewController'),
        ('/api/dashboard/places/overview/', 'GetPlacesOverviewController'),
        (
            '/api/dashboard/places/personal_collections/overview/',
            'GetPersonalCollectionsOverviewController',
        ),
        ('/api/dashboard/blog/articles/overview/', 'GetBlogArticlesOverviewController'),
    ],
)
def test_dashboard_api_paths_resolve_to_current_controllers(
    path: str, controller_name: str
) -> None:
    match = resolve(path)
    resolved_func = cast(Any, match.func)
    assert resolved_func.view_class.__name__ == controller_name
