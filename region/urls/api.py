# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from django.urls import include, path
from dmr.routing import path as dmr_path, Router

from region.api import RegionListByCountryController, search_region, GetRegionsByCountryController

router = Router(
    'api/region',
    [
        dmr_path('list', RegionListByCountryController.as_view(), name='region-list-by-country'),
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
