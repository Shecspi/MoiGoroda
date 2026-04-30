from django.urls import include
from dmr.routing import Router, path

from account.api import (
    GetPersonalVisitedCitiesCountriesCoverageController,
    GetPersonalVisitedCitiesCountriesVisitsController,
    GetPersonalVisitedCitiesOverviewController,
    GetPersonalVisitedCountriesOverviewController,
    GetPersonalVisitedRegionsCountriesCoverageController,
    GetRegionsVisitedCitiesTreemapController,
)

router = Router(
    'api/account',
    [
        path(
            'stats/visited_cities/overview/',
            GetPersonalVisitedCitiesOverviewController.as_view(),
        ),
        path(
            'stats/visited_cities/countries_coverage/',
            GetPersonalVisitedCitiesCountriesCoverageController.as_view(),
        ),
        path(
            'stats/visited_cities/countries_visits/',
            GetPersonalVisitedCitiesCountriesVisitsController.as_view(),
        ),
        path(
            'stats/regions/countries_coverage/',
            GetPersonalVisitedRegionsCountriesCoverageController.as_view(),
        ),
        path(
            'stats/regions/visited_cities_treemap/',
            GetRegionsVisitedCitiesTreemapController.as_view(),
        ),
        path(
            'stats/visited_countries/overview/',
            GetPersonalVisitedCountriesOverviewController.as_view(),
        ),
    ],
)

urlpatterns = [
    path('', include(router.urls)),
]
