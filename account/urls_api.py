from django.urls import include
from dmr.routing import Router, path

from account.api import (
    GetPersonalVisitedCitiesOverviewController,
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
            'stats/regions/visited_cities_treemap/',
            GetRegionsVisitedCitiesTreemapController.as_view(),
        ),
    ],
)

urlpatterns = [
    path('', include(router.urls)),
]
