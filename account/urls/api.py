from django.urls import include
from dmr.routing import Router, path

from account.api import (
    GetPersonalVisitedCitiesCountriesCoverageController,
    GetPersonalVisitedCitiesCountriesVisitsController,
    GetPersonalVisitedCitiesOverviewController,
    GetPersonalVisitedCountriesOverviewController,
    GetPersonalVisitedRegionsCountriesCoverageController,
    GetRegionsVisitedCitiesCountriesController,
    GetRegionsVisitedCitiesTreemapController,
)

router = Router(
    'api/account',
    [
        path(
            'stats/visited-cities/overview/',
            GetPersonalVisitedCitiesOverviewController.as_view(),
        ),
        path(
            'stats/visited-cities/countries-coverage/',
            GetPersonalVisitedCitiesCountriesCoverageController.as_view(),
        ),
        path(
            'stats/visited-cities/countries-visits/',
            GetPersonalVisitedCitiesCountriesVisitsController.as_view(),
        ),
        path(
            'stats/regions/countries-coverage/',
            GetPersonalVisitedRegionsCountriesCoverageController.as_view(),
        ),
        path(
            'stats/regions/visited-cities-treemap/',
            GetRegionsVisitedCitiesTreemapController.as_view(),
        ),
        path(
            'stats/regions/visited-cities-countries/',
            GetRegionsVisitedCitiesCountriesController.as_view(),
        ),
        path(
            'stats/visited-countries/overview/',
            GetPersonalVisitedCountriesOverviewController.as_view(),
        ),
    ],
)

urlpatterns = [
    path('', include(router.urls)),
]
