from django.urls import include, path
from dmr.routing import Router

from region.api import region_list_by_country, search_region, GetRegionsByCountryController

router = Router(
    'api/region',
    [
        path('list', region_list_by_country, name='region-list-by-country'),
        path(
            'list/<str:country_code>/',
            GetRegionsByCountryController.as_view(),
            name='api__region_list_by_code',
        ),
        path('search', search_region, name='search-region'),
    ],
)

urlpatterns = [
    path('', include(router.urls)),
]
